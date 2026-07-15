-- Route a non-empty image *title* to the figure caption (#46, REQ-MDPDF-050).
--
-- The two-field image convention blessed across yf-markdown-lint + yf-markdown-pdf:
--   ![alt](path "title")   alt = accessibility description, title = print caption.
--
-- md2pdf passes NO `-f`, so pandoc's default `markdown` reader is used, which
-- enables `implicit_figures`: an image alone in a paragraph becomes a `Figure`
-- whose caption pandoc derives from the image's ALT text, with the title carried
-- on the inner Image. This filter overrides that: when the image has a non-empty
-- title, the Figure caption becomes the TITLE. Images with no title are left
-- untouched, so pandoc's alt-derived caption stands.
--
-- Reader-neutral by design: this is a render-time Lua filter, so the Markdown
-- source stays pure GFM and the pandoc reader/extensions are unchanged. Do NOT
-- pair it with `-f gfm+implicit_figures` — that would regress md2pdf off full
-- pandoc-markdown.

function Figure(fig)
  local title = nil
  -- Read (not mutate) the title of the first titled image in the figure.
  fig.content:walk {
    Image = function(img)
      if title == nil and img.title and img.title ~= "" then
        title = img.title
      end
    end
  }
  if title == nil then
    return nil  -- no titled image: keep pandoc's default (alt-derived) caption
  end
  -- Parse the title as inline markdown so emphasis/code in a caption render.
  local inlines = pandoc.utils.blocks_to_inlines(pandoc.read(title, "markdown").blocks)
  fig.caption = pandoc.Caption({ pandoc.Plain(inlines) })
  return fig
end
