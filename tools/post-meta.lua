--[[ Post pages (writing/<YYYY-MM-slug>/index.qmd): reading time and previous / next links.
Wired in through writing/_metadata.yml (filters), so it runs on every post; the Writing
listing page itself (writing/index.qmd) is left alone. Pandoc Lua, no dependencies.

- Sets `site-reading-time` ("3 min read", 200 words a minute) for the title-block partial.
- Appends <nav class="site-postnav"> linking to the previous (older) and next (newer) post by
  date. Neighbours are found by reading the front matter of the sibling folders; posts with
  `draft: true` or without a `date` are skipped. Dates are compared as ISO text (YYYY-MM-DD),
  so keep post dates in that form. Links point at the .qmd so Quarto rewrites them to .html.
]]

local path = pandoc.path
local WPM = 200

local function post_dir()
  local input = quarto and quarto.doc and quarto.doc.input_file
  if not input or path.filename(input) ~= "index.qmd" then return nil end
  local dir = path.directory(input)
  local parent = path.directory(dir)
  if path.filename(parent) ~= "writing" then return nil end
  return dir, parent
end

local function front_matter(file)
  local f = io.open(file, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  local fm = text:match("^%-%-%-%s*\n(.-\n)%-%-%-%s*\n") or text:match("^%-%-%-%s*\n(.-\n)%-%-%-%s*$")
  if not fm then return nil end
  local ok, doc = pcall(pandoc.read, "---\n" .. fm .. "---\n", "markdown")
  return ok and doc.meta or nil
end

local function posts(parent)
  local out = {}
  for _, name in ipairs(pandoc.system.list_directory(parent)) do
    local meta = front_matter(path.join({ parent, name, "index.qmd" }))
    if meta and meta.date and not (meta.draft and pandoc.utils.stringify(meta.draft) == "true") then
      table.insert(out, {
        dir = name,
        date = pandoc.utils.stringify(meta.date),
        title = meta.title and pandoc.utils.stringify(meta.title) or name,
      })
    end
  end
  table.sort(out, function(a, b) if a.date ~= b.date then return a.date < b.date end return a.dir < b.dir end)
  return out
end

local function side(cls, label, post)
  return pandoc.Div({ pandoc.Plain({
    pandoc.Span({ pandoc.Str(label) }, { class = "site-postnav__dir" }),
    pandoc.Link({ pandoc.Str(post.title) }, "../" .. post.dir .. "/index.qmd"),
  }) }, { class = cls })
end

function Pandoc(doc)
  local dir, parent = post_dir()
  if not dir then return nil end

  local words = 0
  doc.blocks:walk({ Str = function(s) if s.text:match("%w") then words = words + 1 end end,
                    Code = function(c) words = words + select(2, c.text:gsub("%S+", "")) end,
                    CodeBlock = function(c) words = words + select(2, c.text:gsub("%S+", "")) end })
  doc.meta["site-reading-time"] = pandoc.MetaString(math.max(1, math.ceil(words / WPM)) .. " min read")

  local list, me = posts(parent), path.filename(dir)
  for i, p in ipairs(list) do
    if p.dir == me then
      local items = {}
      if list[i - 1] then table.insert(items, side("site-postnav__prev", "← Previous", list[i - 1])) end
      if list[i + 1] then table.insert(items, side("site-postnav__next", "Next →", list[i + 1])) end
      if #items > 0 then
        doc.blocks:insert(pandoc.RawBlock("html", '<nav class="site-postnav" aria-label="More writing">'))
        doc.blocks:extend(items)
        doc.blocks:insert(pandoc.RawBlock("html", "</nav>"))
      end
      break
    end
  end
  return doc
end
