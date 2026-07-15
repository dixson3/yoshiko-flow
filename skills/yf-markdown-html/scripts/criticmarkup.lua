-- Render CriticMarkup constructs to styled HTML at pandoc time (opt-in).
--
-- md2html.py applies this filter ONLY under --criticmarkup, and only with the
-- `-f gfm-strikeout` reader: under default `gfm`, pandoc parses the inner `~~…~~`
-- of a substitution as `Strikeout` and destroys the construct before any filter
-- runs. Disabling the `strikeout` reader extension lets the whole construct
-- survive as plain `Str`/`Space` tokens for this filter to transform.
--
-- Design (validated against pandoc 3.10, exp-001): an `Inlines` filter that
-- BUFFERS contiguous `Str`/`Space` tokens and, on flush, runs an ordered 5-rule
-- matcher over the joined text — NOT a per-`Str` matcher. A multi-word construct
-- (`{++added several words++}`) splits across many tokens; a per-`Str` filter
-- would only catch single-token cases. Any non-text node (Strong, Code, Link, …)
-- flushes the buffer, so:
--   * inline `Code` / `CodeBlock` are distinct AST nodes that never enter the
--     buffer — a literal `` `{++x++}` `` renders untouched, for free; and
--   * CriticMarkup WRAPPING other inline markup (`{++**bold**++}`) does not
--     transform (the Strong node breaks the buffer) — a documented, accepted edge
--     (CriticMarkup wraps plain prose in practice).
--
-- Escaping: the joined text is HTML-escaped FIRST, then the five patterns match
-- against the escaped delimiter forms (`~>` -> `~&gt;`, `{>>`/`<<}` ->
-- `{&gt;&gt;`/`&lt;&lt;}`). Construct bodies are therefore auto-escaped, and the
-- transformed string is emitted as a single `RawInline("html", …)`.

local ESCAPE = { ["&"] = "&amp;", ["<"] = "&lt;", [">"] = "&gt;" }

local function html_escape(s)
  return (s:gsub("[&<>]", ESCAPE))
end

-- Ordered matcher: substitution FIRST (its `{~~…~>…~~}` must be consumed before
-- the deletion rule could see the `~~`). Patterns run against the escaped string,
-- so bodies captured here are already HTML-escaped.
local RULES = {
  -- substitution: {~~old~>new~~}
  {
    pat = "%{~~(.-)~&gt;(.-)~~%}",
    repl = function(a, b)
      return '<del class="cm-del">' .. a .. "</del><ins class=\"cm-add\">" .. b .. "</ins>"
    end,
  },
  -- addition: {++text++}
  { pat = "%{%+%+(.-)%+%+%}", repl = function(a) return '<ins class="cm-add">' .. a .. "</ins>" end },
  -- deletion: {--text--}
  { pat = "%{%-%-(.-)%-%-%}", repl = function(a) return '<del class="cm-del">' .. a .. "</del>" end },
  -- highlight: {==text==}
  { pat = "%{==(.-)==%}", repl = function(a) return '<mark class="cm-hl">' .. a .. "</mark>" end },
  -- comment: {>>text<<}
  {
    pat = "%{&gt;&gt;(.-)&lt;&lt;%}",
    repl = function(a) return '<span class="cm-comment">' .. a .. "</span>" end,
  },
}

-- Returns (html, matched): the transformed HTML string, and whether any rule fired.
local function transform(text)
  local out = html_escape(text)
  local matched = false
  for _, r in ipairs(RULES) do
    local n
    out, n = out:gsub(r.pat, r.repl)
    if n > 0 then
      matched = true
    end
  end
  return out, matched
end

function Inlines(inlines)
  local result = pandoc.Inlines({})
  local buf = {}

  local function flush()
    if #buf == 0 then
      return
    end
    local joined = table.concat(buf)
    local html, matched = transform(joined)
    if matched then
      result:insert(pandoc.RawInline("html", html))
    else
      -- No construct here: re-emit the original text unchanged (Str + Space) so a
      -- buffer with no CriticMarkup is a no-op — never HTML-escaped needlessly.
      result:insert(pandoc.Str(joined))
    end
    buf = {}
  end

  for _, el in ipairs(inlines) do
    if el.t == "Str" then
      buf[#buf + 1] = el.text
    elseif el.t == "Space" then
      buf[#buf + 1] = " "
    else
      flush()
      result:insert(el)
    end
  end
  flush()
  return result
end
