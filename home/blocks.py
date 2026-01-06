""" StreamField живет здесь"""


from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks import URLBlock


class CardsMenu(blocks.StructBlock):
    external_url = blocks.RichTextBlock(features=['link', 'h4', ], label="ссылка на страницу с оборудованием", required=False)
    # title = blocks.CharBlock(required=True, features=['link', 'h4', ], help_text='заголовок')
    photo = ImageChooserBlock(required=True,)
    # discription = blocks.RichTextBlock(required=False, help_text='описание',)

    class Meta:
        template = 'blocks/menucards.html'
        icon = 'edit'
        label = 'карточки меню'


class DescriptionEquipments(blocks.StructBlock):
    title_diskription_equipment = blocks.RichTextBlock(required=True, features=['link', 'h2', ], help_text='заголовок',)
    podsagolovok = blocks.RichTextBlock(required=True, help_text='подзаголовок на странице с оборудованием')

    class Meta:
        template = 'blocks/breadcramps.html'
        icon = 'edit'
        label = 'заголовок раздела с оборудованием'


class Eqipment_cards(blocks.StructBlock):
    name_equipment = blocks.TextBlock(required=True, max_length=255, help_text='заголовок карточки с оборудованием')
    pfoto_equipment = ImageChooserBlock(required=True,)
    additional_photo_1 = ImageChooserBlock(required=False, help_text='Дополнительное фото 1')
    additional_photo_2 = ImageChooserBlock(required=False, help_text='Дополнительное фото 2')
    additional_photo_3 = ImageChooserBlock(required=False, help_text='Дополнительное фото 3')
    smallname_equipment = blocks.TextBlock(required=False, max_length=255, help_text='заголовок карточки с оборудованием в одно слово')
    description_equipment = blocks.RichTextBlock(required=True, help_text='Брэнд', max_length=255,)
    characteristic_equipment = blocks.RichTextBlock(required=True,  help_text='Характеристики')
    price_equipment = blocks.TextBlock(required=True, help_text='цена (числовое значение, например: 100.50 или 100)',)
    discount_percent = blocks.TextBlock(required=False, help_text='скидка в процентах для этого товара (0-100, например: 10 или 15.5)',)
    quantity_available = blocks.IntegerBlock(required=False, default=0, min_value=0, help_text='количество доступных товаров (0 - товар недоступен)')
    youtube_link = blocks.URLBlock(help_text= 'ссылка на ютуб', required= False)
    promou_equipment = blocks.TextBlock(required=False, help_text='Продвижение',)

    class Meta:
        template = 'blocks/listeq.html'
        icon = 'edit'
        label = 'карточка с оборудованием'


class Carusel(blocks.StructBlock):
    link_band = URLBlock(required=False, help_text='ссылка на группу')
    pfoto_in_carusel = ImageChooserBlock(required=True,)
    interval = blocks.IntegerBlock(required=True, help_text='интервал переключения')

    class Meta:
        template = 'blocks/carusel.html'
        icon = 'edit'
        label = 'редактирование карусели'


class SliderSlideBlock(blocks.StructBlock):
    """Блок для одного слайда"""
    background_image = ImageChooserBlock(
        required=False,
        help_text='Фоновое изображение для слайда'
    )
    slide_text = blocks.RichTextBlock(
        required=False,
        help_text='Текст на слайдере',
        features=['h2', 'h3', 'h4', 'h5', 'p', 'bold', 'italic', 'link', 'ul', 'ol']
    )


class BannerSliderBlock(blocks.StructBlock):
    """Блок для настройки слайдера на главной странице"""
    main_title = blocks.RichTextBlock(
        required=False,
        help_text='Основной заголовок сайта (отображается над слайдером)',
        features=['h1', 'h2', 'bold', 'italic', 'link']
    )
    slider_text = blocks.RichTextBlock(
        required=False,
        help_text='Общий текст для всех слайдов (если не указан индивидуальный текст)',
        features=['h2', 'h3', 'h4', 'h5', 'p', 'bold', 'italic', 'link', 'ul', 'ol']
    )
    background_image_1 = ImageChooserBlock(
        required=False,
        help_text='Фоновое изображение для слайда 1'
    )
    slide_text_1 = blocks.RichTextBlock(
        required=False,
        help_text='Текст для слайда 1',
        features=['h2', 'h3', 'h4', 'h5', 'p', 'bold', 'italic', 'link', 'ul', 'ol']
    )
    background_image_2 = ImageChooserBlock(
        required=False,
        help_text='Фоновое изображение для слайда 2'
    )
    slide_text_2 = blocks.RichTextBlock(
        required=False,
        help_text='Текст для слайда 2',
        features=['h2', 'h3', 'h4', 'h5', 'p', 'bold', 'italic', 'link', 'ul', 'ol']
    )
    background_image_3 = ImageChooserBlock(
        required=False,
        help_text='Фоновое изображение для слайда 3'
    )
    slide_text_3 = blocks.RichTextBlock(
        required=False,
        help_text='Текст для слайда 3',
        features=['h2', 'h3', 'h4', 'h5', 'p', 'bold', 'italic', 'link', 'ul', 'ol']
    )
    background_image_4 = ImageChooserBlock(
        required=False,
        help_text='Фоновое изображение для слайда 4'
    )
    slide_text_4 = blocks.RichTextBlock(
        required=False,
        help_text='Текст для слайда 4',
        features=['h2', 'h3', 'h4', 'h5', 'p', 'bold', 'italic', 'link', 'ul', 'ol']
    )
    background_image_5 = ImageChooserBlock(
        required=False,
        help_text='Фоновое изображение для слайда 5'
    )
    slide_text_5 = blocks.RichTextBlock(
        required=False,
        help_text='Текст для слайда 5',
        features=['h2', 'h3', 'h4', 'h5', 'p', 'bold', 'italic', 'link', 'ul', 'ol']
    )

    class Meta:
        template = 'blocks/banner_slider_block.html'
        icon = 'image'
        label = 'Настройки слайдера'
