---
name: wechat-sticker-pack
description: 规划、编写并校验微信表情专辑或表情单品。用于微信表情包制作、角色一致性与主题内自然差异化提示词、微信表情开放平台上架素材、静态或动态专辑、素材规格检查和上传前 QA；不要用于没有微信表情交付物的通用图片生成。
---

# 微信表情工坊

Create a production-ready plan for a WeChat sticker album or single sticker, or validate an existing upload package. Do not claim that technical validation guarantees platform approval.

## Route the request

- **Create or plan:** build the character baseline, concepts, generation prompts, submission copy, filenames, and QA checklist.
- **Validate assets:** read [references/wechat-official-specs.md](references/wechat-official-specs.md), then run `scripts/validate_sticker_pack.py` on the package.
- **Prepare for upload:** do both. This skill prepares files and guidance; it does not log in, submit, publish, or generate images unless the user separately asks for those actions.
- **Latest/current requirements:** verify the live WeChat Sticker Open Platform first, then state what changed from the bundled reference. Prefer official platform text over third-party summaries.

## Defaults and inputs

- Support sticker albums and single stickers. For an album, accept any requested count from 8 through 24; default to **16 static stickers** when count and mode are omitted.
- A single album must be entirely static or entirely animated. Never mix the two modes.
- Reuse a supplied theme, count, mode, character reference, and intended audience. Ask only when the character cannot be identified well enough to preserve it; otherwise proceed with useful defaults.
- Treat optional reward assets as optional unless the user enables rewards or asks for a complete reward package.

## Creation workflow

1. **Lock the character baseline.** Record silhouette, proportions, face and eye shapes, palette, material or fur, key accessories, line/shading style, and immutable identity traits. If images are supplied, derive the baseline from them.
2. **Define the set.** State static or animated mode, count, theme, audience, tone, and intended chat situations. Cover distinct, reusable meanings rather than near-duplicates.
3. **Plan theme-led variation.** Derive each sticker's scene, pose/action, framing, and composition from this set's theme and chat purpose. Review the set as a whole before writing final prompts so the visual treatments are naturally distinct without drifting away from the theme.
4. **Design each sticker.** Number items consecutively and provide: ASCII filename, meaning word, emotion, scene, pose/action, composition, generation prompt, and character-consistency constraints. Animated prompts must also specify start state, motion, end state, seamless loop, and restrained motion suitable for chat.
5. **Prepare submission copy.** Supply a compliant album name, introduction, copyright attribution, and one meaning word per sticker. Flag any need for copyright or portrait authorization instead of inventing ownership.
6. **Plan supporting assets.** Include the banner, cover, chat-panel icon, and—only when requested—reward guide and reward thank-you images.
7. **Finish with QA.** Separate machine-checkable technical requirements from manual checks for character consistency, readability, originality, rights, content suitability, and set-wide visual repetition.

## Theme-led natural variation

- Choose scenes, poses, actions, props, viewpoints, and compositions because they fit the current theme and intended meaning. Do not use a universal action list, fixed scene catalog, pose quota, or repeated composition template.
- Avoid a set where stickers differ only by caption or facial expression while the body pose, silhouette, viewpoint, and visual relationship remain essentially the same.
- Similar meanings may coexist when their visual expression is clearly distinguishable. Replace items whose silhouette, pose, composition, or scene function is too close to another item.
- Use mainstream popular stickers only as an abstract quality bar: high chat reuse, instantly readable emotion, recognizable action, compact composition, and a coherent rhythm across the set. Do not pursue difference through bizarre poses, abrupt camera angles, irrelevant props, or needlessly complex scenes.
- Keep variation subordinate to the theme. Never add an action, prop, environment, or interaction merely to make an item look different when it weakens the intended chat meaning.

## Prompt and originality rules

- Every sticker prompt must preserve the same identity, proportions, palette, key accessories, and rendering style while allowing expression, pose, props, and camera framing to change.
- Default to one subject per image. Use multiple characters only when the requested concept requires interaction.
- Do not reproduce a specific popular sticker, IP, celebrity, meme image, catchphrase, costume, pose, or composition.
- If the user supplies protected material, distinguish reference ownership from permission to publish. Offer an original alternative when authorization is unclear.

## Deliverable shape

For a creation request, return these sections in Chinese unless the user requests another language:

1. Character baseline
2. Set definition and official-spec summary
3. Sticker table with the requested number of rows, including scene, pose/action, and composition
4. Album metadata and supporting-asset briefs
5. Package layout and filenames
6. Upload QA checklist, including a set-wide repetition review

Use stable, sortable ASCII filenames. Recommended package layout:

```text
sticker-package/
├── main/01_ok_240.png ...
├── banner/banner_750x400.png
├── cover/cover_240.png
├── icon/chat_icon_50.png
└── reward/                 # optional
    ├── guide_750x560.png
    └── thanks_750x750.png
```

Do not require users to prepare 120×120 thumbnails; the current platform flow can generate thumbnails from uploaded stickers.

## Validate a package

Run:

```bash
python3 scripts/validate_sticker_pack.py /path/to/sticker-package
python3 scripts/validate_sticker_pack.py /path/to/sticker-package --json
```

The default layout is shown above. Use `--main-dir`, `--banner`, `--cover`, `--panel-icon`, `--reward-guide`, or `--reward-thanks` to override paths. A nonzero exit code means at least one technical error; warnings still require review but do not fail validation.

Before describing a validator result, distinguish:

- **Error:** incompatible count, dimensions, actual file format, mixed static/animated album, missing required asset, missing transparency, or non-looping animated GIF.
- **Warning:** platform compression may be needed, banner background may be unsuitable, extension differs from actual format, or optional reward assets are incomplete.
- **Manual review:** visual consistency, wording, originality, copyright, portrait rights, and platform content review.
