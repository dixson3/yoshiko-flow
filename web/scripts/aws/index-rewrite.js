// CloudFront viewer-request Function: pretty-URL subdirectory index resolution.
//
// A private S3 bucket read via Origin Access Control does NOT append index.html to
// subdirectory requests — CloudFront's default-root-object only rewrites "/". This
// function makes directory-style pretty URLs resolve:
//
//   /install/     -> /install/index.html   (trailing slash)
//   /install      -> /install/index.html   (extension-less, no slash)
//   /install.sh   -> /install.sh           (has an extension: passes through)
//   /index.html   -> /index.html           (has an extension: passes through)
//   /             -> /index.html           (default-root-object also covers this)
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    if (uri.endsWith('/')) {
        request.uri = uri + 'index.html';
    } else if (uri.lastIndexOf('.') <= uri.lastIndexOf('/')) {
        // No file extension in the last path segment -> treat as a directory.
        request.uri = uri + '/index.html';
    }
    return request;
}
