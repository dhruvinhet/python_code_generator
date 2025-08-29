"""
Professional PowerPoint themes with comprehensive styling options.
Each theme includes color schemes, fonts, backgrounds, and layout preferences.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional

@dataclass
class ColorScheme:
    """Color scheme for a theme"""
    primary: str
    secondary: str
    accent: str
    background_start: str
    background_end: str
    text_primary: str
    text_secondary: str
    text_light: str

    def to_dict(self) -> dict:
        """Convert color scheme to dictionary with hex values"""
        return asdict(self)

@dataclass
class FontScheme:
    """Font scheme for a theme"""
    title_font: str
    content_font: str
    title_size: int
    subtitle_size: int
    content_size: int
    bullet_size: int

@dataclass
class ThemeConfig:
    """Complete theme configuration"""
    name: str
    display_name: str
    description: str
    color_scheme: ColorScheme
    font_scheme: FontScheme
    gradient_angle: int
    icon_style: str  # 'modern', 'classic', 'minimal', 'creative'
    layout_preference: str  # 'balanced', 'text_heavy', 'visual_focused'
    
    def get_css(self) -> str:
        """Generate CSS for the theme"""
        return f"""
            :root {{
                --font-heading: {self.font_scheme.title_font}, system-ui, sans-serif;
                --font-body: {self.font_scheme.content_font}, system-ui, sans-serif;
                --color-primary: {self.color_scheme.primary};
                --color-secondary: {self.color_scheme.secondary};
                --color-accent: {self.color_scheme.accent};
                --color-background-start: {self.color_scheme.background_start};
                --color-background-end: {self.color_scheme.background_end};
                --color-text-primary: {self.color_scheme.text_primary};
                --color-text-secondary: {self.color_scheme.text_secondary};
                --color-text-light: {self.color_scheme.text_light};
            }}
            
            .theme-{self.name} {{
                background: {self.color_scheme.background_start};
                background-image: linear-gradient({self.gradient_angle}deg, {self.color_scheme.background_start}, {self.color_scheme.background_end});
                color: {self.color_scheme.text_primary};
            }}
            
            .theme-{self.name} h1,
            .theme-{self.name} h2,
            .theme-{self.name} h3 {{
                font-family: var(--font-heading);
                color: var(--color-primary);
            }}
            
            .theme-{self.name} p {{
                font-family: var(--font-body);
                font-size: {self.font_scheme.content_size}pt;
            }}
            
            .theme-{self.name} ul,
            .theme-{self.name} ol {{
                font-family: var(--font-body);
                font-size: {self.font_scheme.bullet_size}pt;
            }}
        """

class PPTThemes:
    """Professional PowerPoint themes collection"""

    @staticmethod
    def get_all_themes() -> Dict[str, ThemeConfig]:
        """Get all available themes"""
        return {
            'corporate_blue': PPTThemes._corporate_blue(),
            'modern_gradient': PPTThemes._modern_gradient(),
            'elegant_dark': PPTThemes._elegant_dark(),
            'nature_green': PPTThemes._nature_green(),
            'sunset_warm': PPTThemes._sunset_warm(),
            'ocean_depths': PPTThemes._ocean_depths(),
            'royal_purple': PPTThemes._royal_purple(),
            'minimalist_gray': PPTThemes._minimalist_gray(),
            'vibrant_orange': PPTThemes._vibrant_orange(),
            'tech_cyber': PPTThemes._tech_cyber(),
            'classic_academic': PPTThemes._classic_academic(),
            'creative_rainbow': PPTThemes._creative_rainbow(),
            'financial_gold': PPTThemes._financial_gold(),
            'healthcare_mint': PPTThemes._healthcare_mint(),
            'startup_energy': PPTThemes._startup_energy()
        }

    @staticmethod
    def get_theme(theme_name: str) -> Optional[ThemeConfig]:
        """Get a specific theme by name"""
        themes = PPTThemes.get_all_themes()
        return themes.get(theme_name)

    @staticmethod
    def get_theme_names() -> List[str]:
        """Get list of available theme names"""
        return list(PPTThemes.get_all_themes().keys())

    @staticmethod
    def get_theme_display_info() -> List[Dict]:
        """Get theme information for UI display"""
        themes = PPTThemes.get_all_themes()
        return [
            {
                'id': theme_id,
                'name': theme.display_name,
                'description': theme.description,
                'colors': theme.color_scheme.to_dict(),
                'fonts': {
                    'heading': theme.font_scheme.title_font,
                    'body': theme.font_scheme.content_font
                },
                'gradient_angle': theme.gradient_angle,
                'layout_preference': theme.layout_preference,
                'gradients': {
                    'primary': PPTThemes._generate_gradient_css(
                        theme.color_scheme.primary,
                        theme.color_scheme.secondary,
                        theme.gradient_angle
                    ),
                    'secondary': PPTThemes._generate_gradient_css(
                        theme.color_scheme.secondary,
                        theme.color_scheme.accent,
                        theme.gradient_angle
                    )
                }
            }
            for theme_id, theme in themes.items()
        ]

    @staticmethod
    def _generate_gradient_css(color1: str, color2: str, angle: int) -> str:
        """
        Generates a CSS linear-gradient string from two hex color strings and an angle.
        """
        return f"linear-gradient({angle}deg, {color1}, {color2})"

    @staticmethod
    def _corporate_blue() -> ThemeConfig:
        """Professional corporate blue theme"""
        return ThemeConfig(
            name='corporate_blue',
            display_name='Corporate Blue',
            description='Professional and trustworthy with classic blue tones',
            color_scheme=ColorScheme(
                primary='#0d47a1',
                secondary='#42a5f5',
                accent='#ffc107',
                background_start='#f0f8ff',
                background_end='#e3f2fd',
                text_primary='#212529',
                text_secondary='#6c757d',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=135,
            icon_style='classic',
            layout_preference='balanced'
        )

    @staticmethod
    def _modern_gradient() -> ThemeConfig:
        """Modern gradient theme with contemporary colors"""
        return ThemeConfig(
            name='modern_gradient',
            display_name='Modern Gradient',
            description='Contemporary design with smooth gradients and modern typography',
            color_scheme=ColorScheme(
                primary='#663399',
                secondary='#9c27b0',
                accent='#ff5722',
                background_start='#f8f5ff',
                background_end='#f0e6ff',
                text_primary='#212121',
                text_secondary='#616161',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Light',
                content_font='Segoe UI',
                title_size=40,
                subtitle_size=26,
                content_size=19,
                bullet_size=17
            ),
            gradient_angle=45,
            icon_style='modern',
            layout_preference='visual_focused'
        )

    @staticmethod
    def _elegant_dark() -> ThemeConfig:
        """Elegant dark theme for sophisticated presentations"""
        return ThemeConfig(
            name='elegant_dark',
            display_name='Elegant Dark',
            description='Sophisticated dark theme with gold accents for premium feel',
            color_scheme=ColorScheme(
                primary='#212529',
                secondary='#343a40',
                accent='#ffc107',
                background_start='#343a40',
                background_end='#212529',
                text_primary='#f8f9fa',
                text_secondary='#ced4da',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=90,
            icon_style='minimal',
            layout_preference='text_heavy'
        )

    @staticmethod
    def _nature_green() -> ThemeConfig:
        """Nature-inspired green theme"""
        return ThemeConfig(
            name='nature_green',
            display_name='Nature Green',
            description='Fresh and natural with green tones, perfect for environmental topics',
            color_scheme=ColorScheme(
                primary='#2e7d32',
                secondary='#66bb6a',
                accent='#ffa726',
                background_start='#f8fff8',
                background_end='#e8f5e9',
                text_primary='#1b5e20',
                text_secondary='#4caf50',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=120,
            icon_style='creative',
            layout_preference='balanced'
        )

    @staticmethod
    def _sunset_warm() -> ThemeConfig:
        """Warm sunset theme with orange and red tones"""
        return ThemeConfig(
            name='sunset_warm',
            display_name='Sunset Warm',
            description='Energetic warm tones inspired by sunset colors',
            color_scheme=ColorScheme(
                primary='#e65100',
                secondary='#ff8a65',
                accent='#f44336',
                background_start='#fff8e1',
                background_end='#ffecb3',
                text_primary='#bf360c',
                text_secondary='#ef6c00',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=60,
            icon_style='modern',
            layout_preference='visual_focused'
        )

    @staticmethod
    def _ocean_depths() -> ThemeConfig:
        """Deep ocean theme with blue-teal gradients"""
        return ThemeConfig(
            name='ocean_depths',
            display_name='Ocean Depths',
            description='Deep and calming ocean-inspired blues and teals',
            color_scheme=ColorScheme(
                primary='#004d40',
                secondary='#009688',
                accent='#ffeb3b',
                background_start='#e0f7fa',
                background_end='#b2ebf2',
                text_primary='#004d40',
                text_secondary='#00796b',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Light',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=26,
                content_size=19,
                bullet_size=17
            ),
            gradient_angle=180,
            icon_style='modern',
            layout_preference='balanced'
        )

    @staticmethod
    def _royal_purple() -> ThemeConfig:
        """Luxurious royal purple theme"""
        return ThemeConfig(
            name='royal_purple',
            display_name='Royal Purple',
            description='Luxurious and regal with deep purple and gold combinations',
            color_scheme=ColorScheme(
                primary='#4a148c',
                secondary='#8e24aa',
                accent='#ffc107',
                background_start='#faf5ff',
                background_end='#f3e5f5',
                text_primary='#4a148c',
                text_secondary='#7b1fa2',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=45,
            icon_style='classic',
            layout_preference='text_heavy'
        )

    @staticmethod
    def _minimalist_gray() -> ThemeConfig:
        """Clean minimalist gray theme"""
        return ThemeConfig(
            name='minimalist_gray',
            display_name='Minimalist Gray',
            description='Clean and simple design with subtle gray tones',
            color_scheme=ColorScheme(
                primary='#616161',
                secondary='#9e9e9e',
                accent='#2196f3',
                background_start='#ffffff',
                background_end='#fafafa',
                text_primary='#212121',
                text_secondary='#616161',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Light',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=24,
                content_size=18,
                bullet_size=16
            ),
            gradient_angle=0,
            icon_style='minimal',
            layout_preference='text_heavy'
        )

    @staticmethod
    def _vibrant_orange() -> ThemeConfig:
        """Energetic vibrant orange theme"""
        return ThemeConfig(
            name='vibrant_orange',
            display_name='Vibrant Orange',
            description='Bold and energetic with vibrant orange and complementary colors',
            color_scheme=ColorScheme(
                primary='#e65100',
                secondary='#ff8a65',
                accent='#607d8b',
                background_start='#fff3e0',
                background_end='#ffe0b2',
                text_primary='#bf360c',
                text_secondary='#ef6c00',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=40,
                subtitle_size=30,
                content_size=22,
                bullet_size=20
            ),
            gradient_angle=45,
            icon_style='modern',
            layout_preference='visual_focused'
        )

    @staticmethod
    def _tech_cyber() -> ThemeConfig:
        """Modern tech/cyber theme"""
        return ThemeConfig(
            name='tech_cyber',
            display_name='Tech Cyber',
            description='Futuristic tech theme with neon accents and dark backgrounds',
            color_scheme=ColorScheme(
                primary='#00bcd4',
                secondary='#009688',
                accent='#4caf50',
                background_start='#171c24',
                background_end='#263240',
                text_primary='#e0f7fa',
                text_secondary='#b2ebf2',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=135,
            icon_style='modern',
            layout_preference='visual_focused'
        )

    @staticmethod
    def _classic_academic() -> ThemeConfig:
        """Traditional academic theme"""
        return ThemeConfig(
            name='classic_academic',
            display_name='Classic Academic',
            description='Traditional academic style with serif fonts and conservative colors',
            color_scheme=ColorScheme(
                primary='#8b4513',
                secondary='#cd853f',
                accent='#b22222',
                background_start='#fff8dc',
                background_end='#faf0e6',
                text_primary='#654321',
                text_secondary='#8b4513',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Times New Roman',
                content_font='Times New Roman',
                title_size=36,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=90,
            icon_style='classic',
            layout_preference='text_heavy'
        )

    @staticmethod
    def _creative_rainbow() -> ThemeConfig:
        """Creative rainbow theme for artistic presentations"""
        return ThemeConfig(
            name='creative_rainbow',
            display_name='Creative Rainbow',
            description='Colorful and creative with rainbow gradients for artistic presentations',
            color_scheme=ColorScheme(
                primary='#9c27b0',
                secondary='#673ab7',
                accent='#ffc107',
                background_start='#fff0f5',
                background_end='#f0e6ff',
                text_primary='#4a148c',
                text_secondary='#7b1fa2',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=38,
                subtitle_size=28,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=60,
            icon_style='creative',
            layout_preference='visual_focused'
        )

    @staticmethod
    def _financial_gold() -> ThemeConfig:
        """Professional financial theme with gold accents"""
        return ThemeConfig(
            name='financial_gold',
            display_name='Financial Gold',
            description='Professional financial theme with gold and dark blue for business presentations',
            color_scheme=ColorScheme(
                primary='#0d47a1',
                secondary='#1976d2',
                accent='#ffc107',
                background_start='#fafafa',
                background_end='#f5f5f5',
                text_primary='#0d47a1',
                text_secondary='#1976d2',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI Semibold',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=135,
            icon_style='classic',
            layout_preference='balanced'
        )

    @staticmethod
    def _healthcare_mint() -> ThemeConfig:
        """Clean healthcare theme with mint and blue"""
        return ThemeConfig(
            name='healthcare_mint',
            display_name='Healthcare Mint',
            description='Clean and trustworthy healthcare theme with mint green and blue tones',
            color_scheme=ColorScheme(
                primary='#00796b',
                secondary='#4db6ac',
                accent='#2196f3',
                background_start='#f0fdfa',
                background_end='#e0f7fa',
                text_primary='#004d40',
                text_secondary='#00796b',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=36,
                subtitle_size=26,
                content_size=20,
                bullet_size=18
            ),
            gradient_angle=120,
            icon_style='modern',
            layout_preference='balanced'
        )

    @staticmethod
    def _startup_energy() -> ThemeConfig:
        """High-energy startup theme"""
        return ThemeConfig(
            name='startup_energy',
            display_name='Startup Energy',
            description='Dynamic and energetic theme perfect for startup pitches and innovation',
            color_scheme=ColorScheme(
                primary='#f44336',
                secondary='#ff5722',
                accent='#ffc107',
                background_start='#fff5ee',
                background_end='#ffe0b2',
                text_primary='#b71c1c',
                text_secondary='#f44336',
                text_light='#ffffff'
            ),
            font_scheme=FontScheme(
                title_font='Segoe UI',
                content_font='Segoe UI',
                title_size=40,
                subtitle_size=30,
                content_size=22,
                bullet_size=20
            ),
            gradient_angle=45,
            icon_style='modern',
            layout_preference='visual_focused'
        )