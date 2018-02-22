<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="generator" content="risals; https://github.com/kazh98/risals" />
    <title>{{ title|e }}</title>
{%- if rich %}{% for img in images %}
    <link rel="preload" href="{{ img.thumbnail1_rich }}" as="image" />
{%- endfor %}{% endif %}
  </head>
  <body{% if rich %} class="rich"{% endif %} data-loader-background="{{ images[0].thumbnail2 }}"{% if debug %} data-mode="debug"{% endif %}>
    <script type="text/javascript" src="./lib/00-preloader.js"></script>
    <h1>{{ title|e }}</h1>
    <div class="container">
      <p>
        <a class="button" href="../">Parent Directory</a>
      </p>
      <ul class="gallery">
{%- for img in images %}
        <li>
          <a href="{{ img.filename }}" data-thumbnail="{{ img.thumbnail2 }}">
            <img src="{{ img.thumbnail1 }}" width="{{ img.thumbnail1_width }}" height="{{ img.thumbnail1_height }}" />
          </a>
        </li>
{%- endfor %}
      </ul>
    </div>
    <div class="footer">
last updated on {{ creation_time|e }}.<br />
<a href="{{ generator_url }}">The source code of {{ generator_name|e }} (ver. {{ generator_version|e }})</a> which generated this page is now available.
    </div>
    <script type="text/javascript" src="./lib/01-loader.js"></script>
  </body>
</html>
