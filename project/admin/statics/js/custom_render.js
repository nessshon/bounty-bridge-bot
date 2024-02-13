function renderImageUrl(data, type, full, meta, fieldOptions) {
  function nullOrEmptyColumn() {
    return '<span class="text-center text-muted">-</span>';
  }

  if (!data) return nullOrEmptyColumn();
  if (Array.isArray(data) && data.length === 0) return nullOrEmptyColumn();
  if (type !== "display") return data;

  return '<div class="d-flex"><div class="p-1"><span class="avatar" style="width: 300px; height: 100px; background-image: url(' + data + ')"></span></div></div>';
}

Object.assign(render, {
  image_url: renderImageUrl,
});
