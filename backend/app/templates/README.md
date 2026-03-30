Place your Word template file here:

- Required file name: master_template.docx
- The document should preserve Neil Barot's exact resume layout and formatting.
- Replace mutable experience bullets with Jinja tags, for example:
  - {{bullet_1}}
  - {{bullet_2}}
  - {{bullet_3}}

The API reads bullet defaults from app/data/master_bullets.json.
Create that file by copying app/data/master_bullets.sample.json.
