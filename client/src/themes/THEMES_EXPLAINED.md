# Theming

The theme specifies color of the components, darkness of the surfaces, level of shadow, appropriate opacity of ink elements, etc.

Themes let you apply a consistent tone to your app. It allows you to customize all design aspects of your project in order to meet the specific needs of your business or brand.

Our Theme set consists of four themes: Default, Compact, Flat and Flat Compact. You can check the differences between each of them directly by toggling the "Theme Selector" button positioned on the top-right of our Showcase.

## Theme variables
The base Widgets theme includes the following themable aspects:

**.colors**
This property defines the color palette of the Theme object.

**.typography**
This property defines the variables related to the Font of the Theme object, including Font Family, Font Size and Font Weight.

**.spacing**
This property defines the variables related to the Spacing of the Theme object.

**.applicationStyles**
This property defines the variables related to the overall styles of the Theme object, including shared input styles, label styles, and responsive breakpoints.

**.focusStyles**
This property defines the variables related to the focus styles of the Theme object.

**.divisionLineStyles**
This property defines the variables related to the styles of the dividers of the Theme object, including bottomLine, initialLine, topLine and lineHeight.

**.baseInputStyles**
This property defines the variables related to the Box-Shadow and Line Height styles of the input components inside the Theme object.

**.components**
This property defines the styling variables related to each of the Widget's component. Each of our Component showcase includes a Theme Configuration section for you to take a deeper look on each component's styling configuration values.

There are some differences between each of our theme:

Flat and Flat-Compact themes: Our Flat themes has a explicit color design system comparing to the Default and Compact themes. Therefore, they have some additional .colors values, and a .hoverStyles property.

Compact and Flat-Compact themes: Since they are named as "compact", the .spacing property will have a smaller range of values.

The following example represents our theme object of the current theme.

You can trigger the row action with Enter on a cell.
Property
Type
Value
successColorLight
, belongs tovariant
string
#ecf9eb
warningColor
, belongs tovariant
string
#fcce34
warningColorDark
, belongs tovariant
string
#ad7d04
warningColorLight
, belongs tovariant
string
#fef6db

text
, belongs tovariant
object
error
, belongs totext
string
#fff
warning
, belongs totext
string
#16191d
info
, belongs totext
string
#fff
success
, belongs totext
string
#fff
graphicSecondaryColorDark
, belongs tocolors
string
#7f8c9b
placeHolderBackgroundDark
, belongs tocolors
string
#4e5965
placeHolderBackgroundLight
, belongs tocolors
string
#b7c0c7
boxShadowBackground
, belongs tocolors
string
#16191d
highlightColor
, belongs tocolors
string
#079ae9

highlight
, belongs tocolors
object
greenColor
, belongs tohighlight
string
#067b6f
greenBackgroundLighter
, belongs tohighlight
string
#f0f7f6
greenBackgroundLight
, belongs tohighlight
string
#e8f3f2

status
, belongs tocolors
object
status1Background
, belongs tostatus
string
#ebf5fd
status2Background
, belongs tostatus
string
#c5e9aa
status3Background
, belongs tostatus
string
#f7e455
status2Color
, belongs tostatus
string
#3f572f
status3Color
, belongs tostatus
string
#725d35

typography
, belongs totheme
object

font
, belongs totypography
object
MAIN_FONT
, belongs tofont
string
"open sans", sans-serif
BASE_FONT_SIZE
, belongs tofont
number
1

fontSize
, belongs totypography
object
5XlFontSize
, belongs tofontSize
string
3rem
4XlFontSize
, belongs tofontSize
string
2.25rem
3XlFontSize
, belongs tofontSize
string
1.875rem

# Colors

Our color set consists of the following colors. By using semantic terms instead of explicit color definitions, we guarantee sustainability, maintainability, and consistency throughout our widgets.

## Main Colors
The primary color defines the overall look and feel. It is regularly used for the application header, and content headings.
primaryColor
#fff
The secondary color is a supportive main color and indicates the second-level information. It is used to split primary information for a better overview. Example usages: Main menu, Tab navigation, etc.
secondaryColor
#ebf1f7


## Text Colors
The headline color is used for the title for better contrast to the content.
text.headlineColor
#16191d
The text color is used for the copy, input labels, etc.
text.color
#333
The text secondary color is used for the captions, fine print, less important copy.
text.secondaryColor
#e2e6e9
The text secondary dark color is used for darker captions or fine print.
text.secondaryColorDark
#616f7c
The text inverted color is used for the text on a dark background.
text.invertedColor
#fff
The title color is used for the main titles in the flat theme.
text.titleColor
#202e5d
The placeholder color is used for placeholder text in input fields in the flat theme.
text.placeholderColor
#4d4d4d


## Background Colors
The primary background is used as a background for the main content. Example usages: content area of content boxes.
background.primaryBackground
#fff
The secondary background is used for the body background or a slight visual separation from the primary background.
background.secondaryBackground
#f7fafc
The tertiary background is used for a slight visual separation from primary and secondary backgrounds.
background.tertiaryBackground
#e2e6e9
The interactive background is used for supporting smaller or minor interactive elements.
background.interactiveBackground
#f1f2f4
The non-interactive background is used to visually support smaller or minor non-interactive elements.
background.nonInteractiveBackground
#f9fafb
The inverted background is used for supporting contrary elements.
background.invertedBackground
#fff
The group background is used to support elements that group other elements.
background.groupBackground
#EBF1F7


## Divider Colors
The divider color is used as a divider in lists, border, etc.
divider.color
#e2e6e9
divider.colorSubtle
#becfe2
divider.colorDark
#a9b3bc
divider.colorLight
#fff


## Interaction Colors
The primary interaction color is used for the most prominent action.
interaction.primaryInteractionColor
#00589f
The secondary interaction color is used for the elements which execute an action but with a minor priority.
interaction.secondaryInteractionColor
#00589f
interaction.color
#00589f
interaction.colorDark
#434f67
interaction.colorBG
#ebf1f7
interaction.colorBGLight
#f7fafc


## Interaction States
Active
interaction.active.color
#d50075
interaction.active.colorLight
#ff80c6
Active on Touch
interaction.active.colorTouch
#00589f
interaction.active.colorTouchInverted
#fff
Selected
interaction.selected.color
#00589f
interaction.selected.colorLight
#f5fbff
interaction.selected.colorInverted
#fff
interaction.selected.colorDark
#00589f
Hover
interaction.hover.color
#00589f
interaction.hover.colorInverted
#fff
interaction.hover.colorLight
#80c6ff
Focus
interaction.focus.color
#d50075
interaction.focus.colorInverted
#fff
interaction.focus.outline
none
Draggable
interaction.draggable.color
#00589f
Disabled
interaction.disabled.color
#e2e6e9
interaction.disabled.colorDark
#a9b3bc
interaction.disabled.colorLight
#f1f2f4
Readonly
interaction.readonly.color
#a9b3bc
interaction.readonly.colorDark
#616f7c


## Message Colors
Info
variant.infoColor
#0277bd
variant.infoColorLight
#f6fafe
variant.infoColorLighter
#e5f4ff
variant.infoColorDark
#0277bd
Success
variant.successColor
#2e7d32
variant.successColorLight
#ecf9eb
variant.successColorDark
#2e7d32
Warning
variant.warningColor
#fcce34
variant.warningColorLight
#fef6db
variant.warningColorDark
#ad7d04
Error
variant.errorColor
#c62828
variant.errorColorLight
#fbeaea
variant.errorColorDark
#c62828
Constructive
variant.constructiveColor
#297a24
Destructive
variant.destructiveColor
#c62828
Text
variant.text.info
#fff
variant.text.success
#fff
variant.text.warning
#16191d
variant.text.error
#fff


## Decoration Colors
Box-shadow background
boxShadowBackground
#16191d
Placeholder backgrounds
placeHolderBackgroundDark
#4e5965
placeHolderBackgroundLight
#b7c0c7
Graphic Color
graphicSecondaryColorDark
#7F8C9B


## Highlight Colors
highlightColor
#079ae9
highlightColor.greenColor
#067B6F
highlightColor.greenBackgroundLight
#E8F3F2
highlightColor.greenBackgroundLighter
#F0F7F6


## Status Colors
status1Background
#EBF5FD
status2Background
#C5E9AA
status3Background
#F7E455
status2Color
#3F572F
status3Color
#725D35

# Fonts

Widgets provides a Font System which is used to define the font family, font sizes and font weights.

There are 3 font variables used to control the typography of Widgets:

* Font
* Font Size
* Font Weight
* 
See more about theming and changing Plasma variables here.

## Font
Main Font is used to adjust the font family of an element. Based on typography.font.MAIN_FONT.

All themes that Widgets currently support are using the Main Font of "Open Sans", sans-serif.



## Font Size
Font Size is used to define the font size of an element.

It is calculated based on typography.font.BASE_FONT_SIZE:  

rem

typography.fontSize.5XlFontSize
3rem
A12 Widgets
typography.fontSize.4XlFontSize
2.25rem
A12 Widgets
typography.fontSize.3XlFontSize
1.875rem
A12 Widgets
typography.fontSize.hugeFontSize
1.5rem
A12 Widgets
typography.fontSize.bigFontSize
1.25rem
A12 Widgets
typography.fontSize.lgFontSize
1.125rem
A12 Widgets
typography.fontSize.mediumFontSize
1rem
A12 Widgets
typography.fontSize.smallFontSize
0.875rem
A12 Widgets
typography.fontSize.tinyFontSize
0.75rem
A12 Widgets
typography.fontSize.nanoFontSize
0.625rem
A12 Widgets


## Font Weight

Font Weight is used to define the font weight of an element.

typography.fontWeight.blackFontWeight
900
A12 Widgets
typography.fontWeight.extraBoldFontWeight
800
A12 Widgets
typography.fontWeight.boldFontWeight
700
A12 Widgets
typography.fontWeight.semiBoldFontWeight
600
A12 Widgets
typography.fontWeight.mediumFontWeight
500
A12 Widgets
typography.fontWeight.regularFontWeight
400
A12 Widgets
typography.fontWeight.lightFontWeight
300
A12 Widgets
typography.fontWeight.thinFontWeight
200
A12 Widgets
typography.fontWeight.hairLineFontWeight
100
A12 Widgets

# Spacing

Widgets provides a Spacing System which is used to define the sizes of all components as well as the spacing between them.

There are 3 Plasma spacing variables used to control spacing of all Widgets:

## Spacing
Vertical Spacing
Horizontal Spacing
These variables are also used to further our current Widgets themes:

Default & Flat theme:
Spacing: 16px
Vertical Spacing: 16px
Horizontal Spacing: 16px
Compact & Flat-Compact theme:
Spacing: 12px
Vertical Spacing: 12px
Horizontal Spacing: 12px
See more about theming and changing Plasma variables here.

Spacing
Spacing is used to adjust the width and height of an element. The spacing values are calculated based on the BaseSpacingConfig.BASE.

The following example shows how the spacing values are calculated based on a specific BaseSpacingConfig.BASE value.

BaseSpacingConfig.BASE

px

spacing.spacing.spacing3xs
2px
spacing.spacing.spacing2xs
4px
spacing.spacing.spacingXs
8px
spacing.spacing.spacingSm
12px
spacing.spacing.spacingMd
24px
spacing.spacing.spacingLg
32px
spacing.spacing.spacingXl
52px
spacing.spacing.spacing2Xl
84px


## Vertical Spacing

Vertical Spacing is used to define the vertical margin and vertical padding of an element. The verticalSpacing values are calculate based on BaseSpacingConfig.BASE_VERTICAL_WHITE_SPACING.

The following example shows how the verticalSpacing values are calculated based on a specific BaseSpacingConfig.BASE_VERTICAL_WHITE_SPACING value.

BaseSpacingConfig.BASE_VERTICAL_WHITE_SPACING

px

spacing.verticalSpacing.vertWhiteSpacing3xs
2px
spacing.verticalSpacing.vertWhiteSpacing2xs
4px
spacing.verticalSpacing.vertWhiteSpacingxs
8px
spacing.verticalSpacing.vertWhiteSpacingsm
16px
spacing.verticalSpacing.vertWhiteSpacingmd
24px
spacing.verticalSpacing.vertWhiteSpacinglg
32px
spacing.verticalSpacing.vertWhiteSpacingxl
40px
spacing.verticalSpacing.vertWhiteSpacing2xl
48px
spacing.verticalSpacing.vertWhiteSpacing3xl
56px
spacing.verticalSpacing.vertWhiteSpacing4xl
64px
spacing.verticalSpacing.vertWhiteSpacing5xl
72px
spacing.verticalSpacing.vertWhiteSpacing6xl
80px


## 
Horizontal Spacing

Horizontal Spacing is used to define the horizontal margin and horizontal padding of an element.The horizontalSpacing values are calculate based on BaseSpacingConfig.BASE_HORIZONTAL_WHITE_SPACING.

The following example shows how the horizontalSpacing values are calculated based on a specific BaseSpacingConfig.BASE_HORIZONTAL_WHITE_SPACING value.

