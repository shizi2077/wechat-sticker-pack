#!/usr/bin/env python3
"""Validate a WeChat sticker album package against documented technical specs."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    print("Pillow is required: install it with `python3 -m pip install Pillow`.", file=sys.stderr)
    raise SystemExit(2)


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif"}
FORMAT_EXTENSIONS = {
    "PNG": {".png"},
    "JPEG": {".jpg", ".jpeg"},
    "GIF": {".gif"},
}


@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    path: str
    message: str


class Report:
    def __init__(self, package: Path) -> None:
        self.package = package
        self.issues: list[Issue] = []
        self.files_checked = 0
        self.album_mode: str | None = None

    def add(self, level: str, code: str, path: Path | str, message: str) -> None:
        try:
            display_path = str(Path(path).resolve().relative_to(self.package.resolve()))
        except (ValueError, TypeError):
            display_path = str(path)
        self.issues.append(Issue(level, code, display_path, message))

    def error(self, code: str, path: Path | str, message: str) -> None:
        self.add("error", code, path, message)

    def warning(self, code: str, path: Path | str, message: str) -> None:
        self.add("warning", code, path, message)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.level == "warning"]

    def as_json(self) -> dict[str, object]:
        return {
            "ok": not self.errors,
            "package": str(self.package.resolve()),
            "album_mode": self.album_mode,
            "files_checked": self.files_checked,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [asdict(issue) for issue in self.issues],
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a WeChat sticker album package."
    )
    parser.add_argument("package", type=Path, help="Package root directory")
    parser.add_argument("--main-dir", type=Path, help="Sticker image directory")
    parser.add_argument("--banner", type=Path, help="750x400 banner image")
    parser.add_argument("--cover", type=Path, help="240x240 transparent PNG cover")
    parser.add_argument("--panel-icon", type=Path, help="50x50 transparent PNG icon")
    parser.add_argument("--reward-guide", type=Path, help="Optional 750x560 reward guide")
    parser.add_argument("--reward-thanks", type=Path, help="Optional 750x750 reward thanks")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    return parser.parse_args()


def under_package(package: Path, path: Path | None, default: str) -> Path:
    selected = path or Path(default)
    return selected if selected.is_absolute() else package / selected


def supported_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def resolve_asset(
    report: Report,
    explicit: Path | None,
    directory: str,
    preferred_names: Iterable[str],
    label: str,
    required: bool,
    allow_single_fallback: bool = True,
) -> Path | None:
    if explicit is not None:
        path = under_package(report.package, explicit, "")
        if not path.is_file():
            report.error("MISSING_ASSET", path, f"找不到{label}。")
            return None
        return path

    role_dir = report.package / directory
    for name in preferred_names:
        candidate = role_dir / name
        if candidate.is_file():
            return candidate

    candidates = supported_files(role_dir) if allow_single_fallback else []
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        report.error(
            "AMBIGUOUS_ASSET",
            role_dir,
            f"{label}目录包含多个候选文件；使用对应命令行参数明确指定。",
        )
    elif required:
        report.error("MISSING_ASSET", role_dir, f"缺少{label}。")
    return None


def image_has_transparency(image: Image.Image) -> bool:
    if image.mode in {"RGBA", "LA"}:
        alpha = image.getchannel("A")
        return alpha.getextrema()[0] < 255
    if image.mode == "P" and "transparency" in image.info:
        rgba = image.convert("RGBA")
        return rgba.getchannel("A").getextrema()[0] < 255
    return False


def banner_is_mostly_white(image: Image.Image) -> bool:
    rgb = image.convert("RGB")
    width, height = rgb.size
    if width == 0 or height == 0:
        return False
    step_x = max(1, width // 100)
    step_y = max(1, height // 100)
    points = []
    for x in range(0, width, step_x):
        points.append(rgb.getpixel((x, 0)))
        points.append(rgb.getpixel((x, height - 1)))
    for y in range(0, height, step_y):
        points.append(rgb.getpixel((0, y)))
        points.append(rgb.getpixel((width - 1, y)))
    white = sum(1 for red, green, blue in points if min(red, green, blue) >= 245)
    return bool(points) and white / len(points) >= 0.85


def inspect_image(
    report: Report,
    path: Path,
    *,
    label: str,
    size: tuple[int, int],
    formats: set[str],
    threshold: int,
    require_transparency: bool = False,
    require_gif_loop: bool = False,
    warn_transparency: bool = False,
    warn_white_background: bool = False,
) -> tuple[str | None, bool]:
    if not path.is_file():
        report.error("MISSING_ASSET", path, f"找不到{label}。")
        return None, False

    report.files_checked += 1
    if path.stat().st_size > threshold:
        report.warning(
            "SIZE_COMPRESSION",
            path,
            f"{label}为 {path.stat().st_size / 1024:.1f}KB，超过 {threshold // 1024}KB；平台会尝试压缩，建议预先优化。",
        )

    try:
        with Image.open(path) as image:
            actual_format = (image.format or "").upper()
            animated = actual_format == "GIF" and getattr(image, "n_frames", 1) > 1
            if actual_format not in formats:
                report.error(
                    "FORMAT",
                    path,
                    f"{label}实际格式为 {actual_format or '未知'}，要求：{', '.join(sorted(formats))}。",
                )
            elif path.suffix.lower() not in FORMAT_EXTENSIONS.get(actual_format, set()):
                report.warning(
                    "EXTENSION_MISMATCH",
                    path,
                    f"扩展名 {path.suffix or '(无)'} 与实际格式 {actual_format} 不一致。",
                )
            if image.size != size:
                report.error(
                    "DIMENSIONS",
                    path,
                    f"{label}尺寸为 {image.width}×{image.height}，要求 {size[0]}×{size[1]}。",
                )
            has_transparency = image_has_transparency(image)
            if require_transparency and not has_transparency:
                report.error("TRANSPARENCY", path, f"{label}必须包含透明背景。")
            if warn_transparency and has_transparency:
                report.warning("BANNER_TRANSPARENCY", path, f"{label}不建议使用透明背景。")
            if warn_white_background and banner_is_mostly_white(image):
                report.warning("BANNER_WHITE_BACKGROUND", path, f"{label}边缘大面积接近纯白，官方建议避免白色背景。")
            if require_gif_loop and animated and image.info.get("loop") != 0:
                report.error("GIF_LOOP", path, f"动态{label}必须设置为循环播放。")
            return actual_format, animated
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        report.error("UNREADABLE", path, f"无法读取{label}：{exc}")
        return None, False


def validate_main(report: Report, directory: Path) -> None:
    files = supported_files(directory)
    if not directory.is_dir():
        report.error("MISSING_MAIN_DIR", directory, "缺少主表情目录。")
        return
    if not 8 <= len(files) <= 24:
        report.error("STICKER_COUNT", directory, f"主表情数量为 {len(files)}，要求 8～24 张。")
    if not files:
        return

    modes: list[bool] = []
    for path in files:
        _, animated = inspect_image(
            report,
            path,
            label="主表情",
            size=(240, 240),
            formats={"GIF", "JPEG", "PNG"},
            threshold=500 * 1024,
            require_gif_loop=True,
        )
        modes.append(animated)

    if any(modes) and not all(modes):
        report.album_mode = "mixed"
        report.error("MIXED_MODE", directory, "同一专辑不可混合静态与动态表情。")
    else:
        report.album_mode = "animated" if all(modes) else "static"


def validate_package(args: argparse.Namespace) -> Report:
    package = args.package.expanduser().resolve()
    report = Report(package)
    if not package.is_dir():
        report.error("MISSING_PACKAGE", package, "素材包目录不存在。")
        return report

    main_dir = under_package(package, args.main_dir, "main")
    validate_main(report, main_dir)

    banner = resolve_asset(
        report,
        args.banner,
        "banner",
        ("banner_750x400.png", "banner_750x400.jpg", "banner_750x400.jpeg"),
        "详情页横幅",
        True,
    )
    cover = resolve_asset(report, args.cover, "cover", ("cover_240.png",), "表情封面图", True)
    icon = resolve_asset(report, args.panel_icon, "icon", ("chat_icon_50.png",), "聊天页图标", True)

    if banner:
        inspect_image(
            report,
            banner,
            label="详情页横幅",
            size=(750, 400),
            formats={"JPEG", "PNG"},
            threshold=500 * 1024,
            warn_transparency=True,
            warn_white_background=True,
        )
    if cover:
        inspect_image(
            report,
            cover,
            label="表情封面图",
            size=(240, 240),
            formats={"PNG"},
            threshold=500 * 1024,
            require_transparency=True,
        )
    if icon:
        inspect_image(
            report,
            icon,
            label="聊天页图标",
            size=(50, 50),
            formats={"PNG"},
            threshold=100 * 1024,
            require_transparency=True,
        )

    reward_guide = resolve_asset(
        report,
        args.reward_guide,
        "reward",
        ("guide_750x560.png", "guide_750x560.jpg", "guide_750x560.jpeg", "guide_750x560.gif"),
        "赞赏引导图",
        False,
        False,
    )
    reward_thanks = resolve_asset(
        report,
        args.reward_thanks,
        "reward",
        ("thanks_750x750.png", "thanks_750x750.jpg", "thanks_750x750.jpeg", "thanks_750x750.gif"),
        "赞赏致谢图",
        False,
        False,
    )
    if bool(reward_guide) != bool(reward_thanks):
        missing = "赞赏致谢图" if reward_guide else "赞赏引导图"
        report.warning("INCOMPLETE_REWARD_PAIR", package / "reward", f"赞赏素材不完整，缺少{missing}。")
    if reward_guide:
        inspect_image(
            report,
            reward_guide,
            label="赞赏引导图",
            size=(750, 560),
            formats={"GIF", "JPEG", "PNG"},
            threshold=500 * 1024,
        )
    if reward_thanks:
        inspect_image(
            report,
            reward_thanks,
            label="赞赏致谢图",
            size=(750, 750),
            formats={"GIF", "JPEG", "PNG"},
            threshold=500 * 1024,
        )
    return report


def print_human(report: Report) -> None:
    status = "PASS" if not report.errors else "FAIL"
    print(f"{status}: {report.package}")
    print(f"Mode: {report.album_mode or 'unknown'} | Files checked: {report.files_checked}")
    for issue in report.issues:
        marker = "ERROR" if issue.level == "error" else "WARN"
        print(f"[{marker}] {issue.code} {issue.path}: {issue.message}")
    print(f"Errors: {len(report.errors)} | Warnings: {len(report.warnings)}")
    print("Manual review still required: visual consistency, wording, originality, copyright, portrait rights, and content suitability.")


def main() -> int:
    args = parse_args()
    report = validate_package(args)
    if args.json:
        print(json.dumps(report.as_json(), ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
