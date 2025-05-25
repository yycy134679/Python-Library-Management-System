import customtkinter

# ==============================
# 颜色主题 (Color Palette)
# ==============================
# 主色调
PRIMARY_COLOR = "#0078D4"  # 现代蓝色，替代 #3B8ED0
PRIMARY_COLOR_HOVER = "#005A9E" # 主色调悬停颜色

# 辅助色
SECONDARY_COLOR = "#6c757d"
SECONDARY_COLOR_HOVER = "#545b62"

# 功能性颜色
SUCCESS_COLOR = "#28a745"
DANGER_COLOR = "#dc3545"
DANGER_COLOR_HOVER = "#C82333"
WARNING_COLOR = "#ffc107"
INFO_COLOR = "#17a2b8"

# 背景与文本相关 (基于CustomTkinter的深浅模式)
ERROR_BG_LIGHT = "#FEECEC"
ERROR_BG_DARK = "#4B2525"

# 表格行交替颜色
TABLE_ROW_LIGHT_EVEN = "gray92" 
TABLE_ROW_LIGHT_ODD = "gray98"  
TABLE_ROW_DARK_EVEN = "gray22"  
TABLE_ROW_DARK_ODD = "gray18"   


# ==============================
# 字体 (Typography)
# ==============================
# 字体参数
FONT_DEFAULT_SIZE = 12
FONT_LARGE_SIZE = 14
FONT_XLARGE_SIZE = 16

# 在模块级别将字体变量声明为 None
FONT_NORMAL = None
FONT_BOLD = None
FONT_LARGE_NORMAL = None
FONT_LARGE_BOLD = None
FONT_XLARGE_BOLD = None
FONT_BUTTON = None
FONT_ENTRY_LABEL = None
FONT_TABLE_HEADER = None
FONT_TABLE_CELL = None
FONT_STATUS_BAR = None
FONT_DIALOG_TITLE = None
FONT_ERROR_TEXT = None

def initialize_fonts():
    """
    Initializes all CTkFont objects.
    This function MUST be called after the customtkinter.CTk() main window is initialized.
    """
    global FONT_NORMAL, FONT_BOLD, FONT_LARGE_NORMAL, FONT_LARGE_BOLD, FONT_XLARGE_BOLD
    global FONT_BUTTON, FONT_ENTRY_LABEL, FONT_TABLE_HEADER, FONT_TABLE_CELL
    global FONT_STATUS_BAR, FONT_DIALOG_TITLE, FONT_ERROR_TEXT

    # 主字体 (通常使用CTk默认，这里定义特定用途的)
    FONT_NORMAL = customtkinter.CTkFont(size=FONT_DEFAULT_SIZE)
    FONT_BOLD = customtkinter.CTkFont(size=FONT_DEFAULT_SIZE, weight="bold")

    FONT_LARGE_NORMAL = customtkinter.CTkFont(size=FONT_LARGE_SIZE)
    FONT_LARGE_BOLD = customtkinter.CTkFont(size=FONT_LARGE_SIZE, weight="bold")

    FONT_XLARGE_BOLD = customtkinter.CTkFont(size=FONT_XLARGE_SIZE, weight="bold")

    # 特定组件字体
    FONT_BUTTON = customtkinter.CTkFont(size=FONT_DEFAULT_SIZE) # 或 FONT_NORMAL
    FONT_ENTRY_LABEL = customtkinter.CTkFont(size=FONT_DEFAULT_SIZE) # 或 FONT_NORMAL
    FONT_TABLE_HEADER = customtkinter.CTkFont(size=FONT_LARGE_SIZE, weight="bold") # 或 FONT_LARGE_BOLD
    FONT_TABLE_CELL = customtkinter.CTkFont(size=FONT_DEFAULT_SIZE) # 或 FONT_NORMAL
    FONT_STATUS_BAR = customtkinter.CTkFont(size=FONT_DEFAULT_SIZE) # 或 FONT_NORMAL
    FONT_DIALOG_TITLE = customtkinter.CTkFont(size=FONT_XLARGE_SIZE, weight="bold") # 或 FONT_XLARGE_BOLD
    FONT_ERROR_TEXT = customtkinter.CTkFont(size=FONT_DEFAULT_SIZE) # 或 FONT_NORMAL


# ==============================
# 间距与布局 (Spacing & Layout)
# ==============================
PAD_X_SMALL = 5
PAD_Y_SMALL = 5

PAD_X_MEDIUM = 10
PAD_Y_MEDIUM = 10

PAD_X_LARGE = 15
PAD_Y_LARGE = 15

PAD_X_XLARGE = 20
PAD_Y_XLARGE = 20

# 组件内部间距
INNER_PAD_X_BUTTON = 10
INNER_PAD_Y_BUTTON = 5

# ==============================
# 圆角 (Corner Radius)
# ==============================
CORNER_RADIUS_BUTTON = 6
CORNER_RADIUS_ENTRY = 6
CORNER_RADIUS_FRAME = 8
CORNER_RADIUS_DIALOG = 10 
CORNER_RADIUS_TABLE_HEADER = 6
CORNER_RADIUS_ERROR_LABEL = 4

# ==============================
# 组件尺寸 (Component Sizes)
# ==============================
HEIGHT_BUTTON = 32
HEIGHT_ENTRY = 30
HEIGHT_OPTIONMENU = 30
HEIGHT_TOOLBAR_BUTTON = 32 
HEIGHT_TABLE_ROW_ACTION_BUTTON = 28 

WIDTH_TABLE_ROW_ACTION_BUTTON = 70