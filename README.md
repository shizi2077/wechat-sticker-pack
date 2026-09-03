# 微信表情工坊 🧩

> 角色一致，表达不重复，规格可验证。把一个角色做成真正能聊天、能上架的微信表情包。

**微信表情工坊**是一套面向 Codex 与其他 Agent Skills 兼容智能体的微信表情包制作 Skill。它从角色基准、主题策划和提示词编排开始，帮助整套表情保持统一角色与画风，同时让每张表情的场景、姿势和构图产生自然、主题相关的差异；完成创作后，还能依据微信表情开放平台规格检查上传素材。

## 它能做什么

- **角色一致**：锁定轮廓、比例、配色、材质、关键配饰和画风，减少批量生成时的角色漂移。
- **自然差异化**：根据每套主题安排不同场景、姿势、动作与构图，避免只换文字或表情，不使用僵硬的固定动作清单。
- **主流易读**：参考热门表情包的聊天复用性、情绪可读性和紧凑构图，但不复制具体 IP、台词、姿势或画面。
- **上架规格**：覆盖静态与动态专辑、表情单品、横幅、封面、聊天页图标及可选赞赏素材。
- **自动校验**：检查数量、尺寸、真实格式、体积、透明度、静动态混用及 GIF 循环设置，并输出普通报告或 JSON。

## 什么时候使用

- 为宠物、原创角色、品牌吉祥物或参考图设计微信表情包；
- 生成主题统一、角色一致且视觉表达不重复的整套提示词；
- 准备微信表情开放平台的专辑文案和配套素材；
- 在上传前检查图片尺寸、格式、透明度和文件结构；
- 排查微信表情素材包中的技术问题。

普通图片生成、没有微信表情交付物的任务不需要使用本 Skill。

## 安装

使用 Agent Skills CLI：

```bash
npx skills add shizi2077/wechat-sticker-pack --skill wechat-sticker-pack
```

在 Codex 中，也可以让 `$skill-installer` 从以下位置安装：

```text
仓库：shizi2077/wechat-sticker-pack
路径：wechat-sticker-pack
```

或将仓库中的 `wechat-sticker-pack` 目录复制到 `~/.codex/skills/`。

## 使用示例

```text
使用 $wechat-sticker-pack，把这只猫设计成一套 16 张的微信表情包。
主题是“嘴硬但黏人”，保持角色一致，每张的场景、姿势和构图要自然区分。
```

检查已有素材包：

```bash
python3 ~/.codex/skills/wechat-sticker-pack/scripts/validate_sticker_pack.py /path/to/sticker-package
```

输出 JSON：

```bash
python3 ~/.codex/skills/wechat-sticker-pack/scripts/validate_sticker_pack.py /path/to/sticker-package --json
```

## 核心原则

1. 先锁定角色，再设计表情。
2. 差异化服从主题，不为了不同而猎奇。
3. 相似含义可以保留，但视觉表达必须可辨识。
4. 参考主流表情包的功能与节奏，不复刻具体作品。
5. 技术校验不能替代版权、肖像权、视觉质量和平台审核。

## 仓库结构

```text
wechat-sticker-pack/
├── SKILL.md
├── agents/openai.yaml
├── references/wechat-official-specs.md
└── scripts/validate_sticker_pack.py
```

微信平台规则可能更新。Skill 内置规格核验日期为 2026-09-03；准备立即投稿或查询最新要求时，应以[微信表情开放平台](https://sticker.weixin.qq.com/cgi-bin/mmemoticonwebnode-bin/pages/home)实时页面为准。

## 名字的意思

“微信表情工坊”强调的是一套完整制作流程：不只写提示词，也不只检查尺寸，而是把角色设定、主题表达、整套差异化和上架校验连成一条可复用的工作流。

## License

MIT

