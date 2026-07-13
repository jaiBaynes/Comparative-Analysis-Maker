import pygame
import os
import glob
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple


# Default layout constants (easy to tweak)
DEFAULT_CANVAS_SIZE = (1080, 1350)
DEFAULT_LEFT_MARGIN = 40
DEFAULT_TOP_MARGIN = 40
DEFAULT_NAME_COL = 260
DEFAULT_ROW_HEIGHT = 56
DEFAULT_FEATURE_SIZE = 28
DEFAULT_FEATURE_SPACING = 60
DEFAULT_LEGEND_HEIGHT = 140
DEFAULT_FONT_SIZE = 15
DEFAULT_TITLE_FONT_SIZE = 36
DEFAULT_TOP_IMAGE_SPACE = 500
DEFAULT_SWATCH_SPACING = 170
DEFAULT_UNDERLINE_OFFSET = 6
DEFAULT_UNDERLINE_THICKNESS = 4

# default marker colors
DEFAULT_PERFECT_MARKER_COLOR = (0, 0, 0)
DEFAULT_PARTIAL_MARKER_COLOR = (0, 0, 0)
DEFAULT_NONE_MARKER_COLOR = (0, 0, 0)


class FeatureStatus(Enum):
    NONE = 0
    PARTIAL = 1
    PERFECT = 2


@dataclass
class Comparand:
    name: str
    feature_states: List[FeatureStatus] = field(default_factory=list)
    color: Tuple[int, int, int] = (200, 50, 50)  # accent color for this comparand (unused for features)

    def match_score(self) -> Tuple[float, float]:
        """Return (points_scored, percent) where partial counts as 0.5 point."""
        if not self.feature_states:
            return 0.0, 0.0
        perfect = sum(1 for s in self.feature_states if s == FeatureStatus.PERFECT)
        partial = sum(1 for s in self.feature_states if s == FeatureStatus.PARTIAL)
        points = perfect + 0.5 * partial
        percent = (points / len(self.feature_states)) * 100.0
        return points, percent


class Visualizer:
    def __init__(
        self,
        feature_labels: List[str],
        canvas_size: Tuple[int, int] = DEFAULT_CANVAS_SIZE,
        top_image_space: int = DEFAULT_TOP_IMAGE_SPACE,
        left_margin: int = DEFAULT_LEFT_MARGIN,
        top_margin: int = DEFAULT_TOP_MARGIN,
        name_col: int = DEFAULT_NAME_COL,
        row_height: int = DEFAULT_ROW_HEIGHT,
        feature_size: int = DEFAULT_FEATURE_SIZE,
        feature_spacing: int = DEFAULT_FEATURE_SPACING,
        legend_height: int = DEFAULT_LEGEND_HEIGHT,
        font_size: int = DEFAULT_FONT_SIZE,
        title_font_size: int = DEFAULT_TITLE_FONT_SIZE,
        swatch_spacing: int = DEFAULT_SWATCH_SPACING,
        underline_offset: int = DEFAULT_UNDERLINE_OFFSET,
        underline_thickness: int = DEFAULT_UNDERLINE_THICKNESS,
        perfect_marker_color: Tuple[int, int, int] = DEFAULT_PERFECT_MARKER_COLOR,
        partial_marker_color: Tuple[int, int, int] = DEFAULT_PARTIAL_MARKER_COLOR,
        none_marker_color: Tuple[int, int, int] = DEFAULT_NONE_MARKER_COLOR,
    ):
        pygame.init()
        self.feature_labels = feature_labels[:12]
        self.n_features = max(1, len(self.feature_labels))

        # canvas and layout (all adjustable via parameters)
        self.canvas_width, self.canvas_height = canvas_size
        self.left_margin = left_margin
        self.top_margin = top_margin
        self.name_col = name_col
        self.row_height = row_height
        self.feature_size = feature_size
        self.feature_spacing = feature_spacing
        self.legend_height = legend_height
        self.font = pygame.font.SysFont(None, font_size)
        self.title_font = pygame.font.SysFont(None, title_font_size)
        self.top_image_space = top_image_space
        self.swatch_spacing = swatch_spacing
        self.underline_offset = underline_offset
        self.underline_thickness = underline_thickness
        self.perfect_marker_color = perfect_marker_color
        self.partial_marker_color = partial_marker_color
        self.none_marker_color = none_marker_color

        # default feature colors (12 distinct colors)
        self.feature_colors = [
            (220, 20, 60),
            (255, 140, 0),
            (255, 215, 0),
            (34, 139, 34),
            (0, 128, 255),
            (75, 0, 130),
            (199, 21, 133),
            (160, 82, 45),
            (70, 130, 180),
            (128, 0, 0),
            (0, 100, 0),
            (128, 0, 128),
        ]

    def _calc_size(self, n_comparands: int) -> Tuple[int, int]:
        # use fixed canvas size requested by user
        return self.canvas_width, self.canvas_height

    def draw_legend(self, surface: pygame.Surface, x: int, y: int):
        title = self.title_font.render('Legend', True, (20, 20, 20))
        surface.blit(title, (x, y))
        y += 40

        # feature swatches
        for i, label in enumerate(self.feature_labels):
            cx = x + (i % 6) * self.swatch_spacing
            cy = y + (i // 6) * (self.font.get_linesize() + 8)
            color = self.feature_colors[i % len(self.feature_colors)]
            rect = pygame.Rect(cx, cy, 24, 24)
            pygame.draw.rect(surface, color, rect)
            lbl = self.font.render(label, True, (30, 30, 30))
            surface.blit(lbl, (cx + 34, cy + 4))

        # symbol legend (below feature swatches)
        sy = y + ((len(self.feature_labels) - 1) // 6 + 1) * (self.font.get_linesize() + 8) + 18
        sym_x = x
        # perfect: filled rectangle (marker color)
        pr = pygame.Rect(sym_x, sy, self.feature_size, self.feature_size)
        pygame.draw.rect(surface, self.perfect_marker_color, pr)
        pygame.draw.rect(surface, (0, 0, 0), pr, 2)
        surface.blit(self.font.render('Perfect match (filled rectangle)', True, (30, 30, 30)), (sym_x + self.feature_size + 14, sy + 2))

        # partial: filled circle with underline
        sym_x += 360
        center = (sym_x + 12, sy + 12)
        pygame.draw.circle(surface, self.partial_marker_color, center, self.feature_size // 2)
        pygame.draw.circle(surface, (0, 0, 0), center, self.feature_size // 2, 2)
        ul_start = (center[0] - self.feature_size // 2 + 3, center[1] + self.feature_size // 2 + self.underline_offset)
        ul_end = (center[0] + self.feature_size // 2 - 3, center[1] + self.feature_size // 2 + self.underline_offset)
        pygame.draw.line(surface, self.partial_marker_color, ul_start, ul_end, self.underline_thickness)
        surface.blit(self.font.render('Partial / disputed (underlined filled circle)', True, (30, 30, 30)), (sym_x + self.feature_size + 14, sy + 2))

        # none: empty square outline
        sym_x += 480
        nr = pygame.Rect(sym_x, sy, self.feature_size, self.feature_size)
        pygame.draw.rect(surface, (230, 230, 230), nr)
        pygame.draw.rect(surface, (120, 120, 120), nr, 2)
        # draw X with none marker color
        pygame.draw.line(surface, self.none_marker_color, (sym_x + 3, sy + 3), (sym_x + self.feature_size - 3, sy + self.feature_size - 3), 2)
        pygame.draw.line(surface, self.none_marker_color, (sym_x + self.feature_size - 3, sy + 3), (sym_x + 3, sy + self.feature_size - 3), 2)
        surface.blit(self.font.render('No match (X)', True, (30, 30, 30)), (sym_x + self.feature_size + 14, sy + 2))

    def draw_definition(self, surface: pygame.Surface, x: int, y: int, max_width: int, text: str):
        # simple word-wrapping then draw lines
        words = text.split()
        lines = []
        cur = ''
        for w in words:
            test = cur + (' ' if cur else '') + w
            if self.font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        for i, line in enumerate(lines):
            surf = self.font.render(line, True, (25, 25, 25))
            surface.blit(surf, (x, y + i * (self.font.get_linesize() + 2)))

    def draw_comparand_row(self, surface: pygame.Surface, comparand: Comparand, index: int, x: int, y: int):
        # name
        name_surf = self.font.render(comparand.name, True, (10, 10, 10))
        surface.blit(name_surf, (x + 4, y + (self.row_height - name_surf.get_height()) // 2))

        # score: show fraction and percentage
        points, percent = comparand.match_score()
        if points.is_integer():
            pts_text = f"{int(points)}/{len(comparand.feature_states)}"
        else:
            pts_text = f"{points:.1f}/{len(comparand.feature_states)}"
        score_text = f"{pts_text} = {int(round(percent))}%"
        score_surf = self.font.render(score_text, True, (80, 80, 80))
        surface.blit(score_surf, (x + self.name_col - 120, y + (self.row_height - score_surf.get_height()) // 2))

        # feature markers -- dynamic spacing to fit all features in available width
        start_x = x + self.name_col
        cy = y + self.row_height // 2

        # estimate available width to the right edge of column
        # assume columns are half the canvas width (render_columns uses half); fallback to canvas width
        col_right = x + (self.canvas_width - 2 * self.left_margin) // 2 if x > self.left_margin else self.canvas_width - self.left_margin
        available = max(200, col_right - start_x - 20)
        eff_spacing = max(6, available // max(1, self.n_features))
        eff_feature_size = min(self.feature_size, int(eff_spacing * 0.75))

        for i in range(self.n_features):
            fx = start_x + i * eff_spacing
            state = comparand.feature_states[i] if i < len(comparand.feature_states) else FeatureStatus.NONE
            feature_color = self.feature_colors[i % len(self.feature_colors)]

            if state == FeatureStatus.PERFECT:
                rect = pygame.Rect(fx, cy - eff_feature_size // 2, eff_feature_size, eff_feature_size)
                pygame.draw.rect(surface, feature_color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 2)
            elif state == FeatureStatus.PARTIAL:
                # draw filled circle and an underline using feature color
                center = (fx + eff_feature_size // 2, cy)
                pygame.draw.circle(surface, feature_color, center, eff_feature_size // 2)
                pygame.draw.circle(surface, (0, 0, 0), center, eff_feature_size // 2, 2)
                ul_start = (center[0] - eff_feature_size // 2 + 2, center[1] + eff_feature_size // 2 + self.underline_offset)
                ul_end = (center[0] + eff_feature_size // 2 - 2, center[1] + eff_feature_size // 2 + self.underline_offset)
                pygame.draw.line(surface, feature_color, ul_start, ul_end, max(1, self.underline_thickness - 1))
            else:
                # NONE -> empty gray square outline and an X in none_marker_color
                rect = pygame.Rect(fx, cy - eff_feature_size // 2, eff_feature_size, eff_feature_size)
                pygame.draw.rect(surface, (230, 230, 230), rect)
                pygame.draw.rect(surface, (120, 120, 120), rect, 1)
                pygame.draw.line(surface, self.none_marker_color, (fx + 2, cy - eff_feature_size // 2 + 2), (fx + eff_feature_size - 2, cy + eff_feature_size // 2 - 2), 1)
                pygame.draw.line(surface, self.none_marker_color, (fx + eff_feature_size - 2, cy - eff_feature_size // 2 + 2), (fx + 2, cy + eff_feature_size // 2 - 2), 1)

    def render(self, comparands: List[Comparand], title: str = 'Comparative Analysis'):
        # backward-compatible single-column render moved to two-column API below
        raise RuntimeError('Use render_columns(left_list, right_list=None, title=...) or export_image(...)')

    def render_to_surface(self, left_list: List[Comparand], right_list: List[Comparand] = None, title: str = 'Comparative Analysis') -> pygame.Surface:
        # create an off-screen surface and draw the full layout once
        surface = pygame.Surface((self.canvas_width, self.canvas_height))
        surface.fill((246, 236, 227))

        # title
        title_surf = self.title_font.render(title, True, (15, 15, 15))
        surface.blit(title_surf, (self.left_margin, 8))

        # definition
        def_text = (
            'Comparands: Figures or plots that contain vague similarities but distinct differences across cultures. '
            'Unlike cognates, these figures share thematic or aesthetic traits that outlive their originals.'
        )
        self.draw_definition(surface, self.left_margin, 48, self.canvas_width - self.left_margin * 2, def_text)

        # legend
        self.draw_legend(surface, self.left_margin, self.top_margin + 120)

        # compute top y for comparand rows
        start_y = self.top_margin + self.legend_height + self.top_image_space

        # layout columns
        col_width = (self.canvas_width - 2 * self.left_margin) // 2
        left_x = self.left_margin
        right_x = self.left_margin + col_width

        left_list = left_list or []
        right_list = right_list or []

        max_rows = max(len(left_list), len(right_list))
        for idx in range(max_rows):
            # left row
            if idx < len(left_list):
                row_y = start_y + idx * self.row_height
                row_rect = pygame.Rect(left_x - 10, row_y - 6, col_width - 10, self.row_height - 4)
                pygame.draw.rect(surface, (255, 255, 255), row_rect)
                pygame.draw.rect(surface, (220, 220, 220), row_rect, 1)
                self.draw_comparand_row(surface, left_list[idx], idx, left_x, row_y)

            # right row
            if idx < len(right_list):
                row_y = start_y + idx * self.row_height
                row_rect = pygame.Rect(right_x - 10, row_y - 6, col_width - 10, self.row_height - 4)
                pygame.draw.rect(surface, (255, 255, 255), row_rect)
                pygame.draw.rect(surface, (220, 220, 220), row_rect, 1)
                self.draw_comparand_row(surface, right_list[idx], idx, right_x, row_y)

        return surface

    def render_columns(self, left_list: List[Comparand], right_list: List[Comparand] = None, title: str = 'Comparative Analysis'):
        width, height = self._calc_size(0)
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Comparative Analysis Visualizer')

        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            surf = self.render_to_surface(left_list, right_list, title)
            screen.blit(surf, (0, 0))
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

    def export_image(self, left_list: List[Comparand], right_list: List[Comparand] = None, title: str = 'Comparative Analysis', out_dir: str = 'output_images') -> str:
        surf = self.render_to_surface(left_list, right_list, title)
        # ensure output dir
        os.makedirs(out_dir, exist_ok=True)
        pattern = os.path.join(out_dir, 'comparison_*.png')
        existing = glob.glob(pattern)
        max_idx = 0
        for p in existing:
            m = re.search(r'comparison_(\d+)\.png$', p)
            if m:
                try:
                    v = int(m.group(1))
                    if v > max_idx:
                        max_idx = v
                except ValueError:
                    pass
        next_idx = max_idx + 1
        filename = f'comparison_{next_idx:03d}.png'
        path = os.path.join(out_dir, filename)
        pygame.image.save(surf, path)
        return path


if __name__ == '__main__':
    # small runnable demo
    features = [
        'king of gods', 'eagle association', 'lustful/seducer', 'cognates', 'fight serpent',
        'storm god powers', 'thunderbolt weapon', 'fight giants', 'fought/overthrew father',
        'shape shifter', 'mountain/top home', 'uncertain/disputed'
    ]

    viz = Visualizer(features)

    a = Comparand('JUPITER (Roman)', [FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                      FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                      FeatureStatus.PERFECT, FeatureStatus.NONE, FeatureStatus.PERFECT,
                                      FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PERFECT])

    b = Comparand('THOR / THUNAR (Norse)', [FeatureStatus.PERFECT, FeatureStatus.NONE, FeatureStatus.PARTIAL,
                                            FeatureStatus.NONE, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                            FeatureStatus.PERFECT, FeatureStatus.PARTIAL, FeatureStatus.NONE,
                                            FeatureStatus.NONE, FeatureStatus.NONE, FeatureStatus.PARTIAL])

    c = Comparand('INDRA (Vedic)', [FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.PARTIAL,
                                    FeatureStatus.NONE, FeatureStatus.PERFECT, FeatureStatus.PERFECT,
                                    FeatureStatus.PERFECT, FeatureStatus.PERFECT, FeatureStatus.NONE,
                                    FeatureStatus.NONE, FeatureStatus.NONE, FeatureStatus.PARTIAL])

    viz.render([a, b, c], title='The Many Other ZEUSes (demo)')
