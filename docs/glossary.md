# Glossary

Technical terms used across the reference pages. Confidence levels and the
meaning of `selected` and `accepted` are defined in the
[evidence model](evidence-model.md).

| Term | Meaning |
|---|---|
| Guest | The original Xbox 360 game code, as opposed to the recompiled runtime. |
| Image | The supported game executable, identified in [the image manifest](../manifests/image.json). |
| VA | Virtual address: where code or data sits in guest memory, written `0x82E2943C`. |
| `RVA-F-`, `RVA-SYM-`, ... | Finding and catalog ID prefixes, for example `RVA-F-0363`. See [catalogs](catalogs.md#identity-and-formats). |
| `sub_XXXXXXXX`, `DAT_XXXXXXXX` | A guest function or data address that has no recovered name yet. |
| vtable | A table of function pointers that a C++ object uses to call its methods. |
| Manifest | A record of one investigated topic, with its claims, locators and limits. See [topic manifests](topic-manifests.md). |
| Catalog | A shared index of reusable entities (functions, structures, enums) and their relations. See [catalogs](catalogs.md). |
| Locator | The exact address, offset or source reference that backs a claim. |
| Hook point | A place where a mod or the runtime could change native behavior. |
