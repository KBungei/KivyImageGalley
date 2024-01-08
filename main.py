from kivy.app import App

from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.behaviors import FocusBehavior

from modules.scan_path import scan_path_for_images, check_path_is_image
from modules.batch_iterator import batch_iterator


class FullScreenView(Screen):
    image_path = StringProperty('')

    def __init__(self, **kwargs):
        super(FullScreenView, self).__init__(**kwargs)
        self.bind(image_path=self.display_image)

    def display_image(self, instance, value):
        self.clear_widgets()
        path = value

        if check_path_is_image(path):
            image_wid = AsyncImage(
                    source=path,
                )
            self.add_widget(image_wid)
            image_wid.on_touch_down = self.switch_to_gallery

    def switch_to_gallery(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            screen_manager = app.root
            screen_manager.switch_to_scr('gallery')


class ImageWidget(AsyncImage):
    image_path = StringProperty('')
    pressed = ListProperty([0, 0])

    def __init__(self, path, **kwargs):
        super(ImageWidget, self).__init__(**kwargs)
        self.image_path = path

        self.on_touch_down = self.view_full

    def view_full(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            screen_manager = app.root

            full_screen = screen_manager.av_screens['full_screen']
            full_screen.image_path = self.image_path

            screen_manager.switch_to_scr('full_screen')


class GalleryView(Screen, FocusBehavior):
    paths = ListProperty([])
    curr_batch = ListProperty([])

    def __init__(self, **kwargs):
        super(GalleryView, self).__init__(**kwargs)

        self.bind(paths=self.init_gallery)

    def init_gallery(self, instance, value):
        self.batch_iter = batch_iterator(value, 4)
        self.bind(curr_batch=self.display_batch)

        self.curr_batch = self.get_batch()

    def get_batch(self):
        try:
            batch = next(self.batch_iter)
            print(batch)
            return batch

        except StopIteration:
            return []

    def display_batch(self, instance, value):
        self.clear_widgets()
        gallery_container = FloatLayout()

        gallery_grid = GridLayout()
        gallery_grid.cols = 2

        if value != []:
            for path in value:

                image_wid = ImageWidget(
                        path,
                        source=path,
                    )

                gallery_grid.add_widget(image_wid)

            gallery_container.add_widget(gallery_grid)

            prev_btn = Button(
                text='<',
                pos_hint={'x': 0, 'y': .455},
                size_hint=(.1, .1),
            )

            nxt_btn = Button(
                text='>',
                pos_hint={'x': .9, 'y': .455},
                size_hint=(.1, .1),
            )

            nxt_btn.on_press = self.get_nxt

            gallery_container.add_widget(prev_btn)
            gallery_container.add_widget(nxt_btn)

            self.add_widget(gallery_container)
            self.focus = True

        else:
            self.add_widget(Label(text='The END!'))

    def get_nxt(self):
        self.curr_batch = self.get_batch()

    def on_key_down(self, instance, key, keycode, text, modifiers):
        if key == 'left':
            print('LEFT KEY PRESSSSSED!')


class ScrManager(ScreenManager):
    av_screens = ObjectProperty({})
    sw_directions = ObjectProperty({
        'gallery': 'right',
        'full_screen': 'left'
    })

    def __init__(self, **kwargs):
        super(ScrManager, self).__init__(**kwargs)

    def add_widget(self, widget, *args, **kwargs):
        scr_name = widget.name

        self.av_screens[scr_name] = widget
        return super().add_widget(widget, *args, **kwargs)

    def switch_to_scr(self, scr_name):
        av_screens = self.av_screens
        sw_directions = self.sw_directions

        if scr_name in av_screens.keys():

            if scr_name in sw_directions.keys():
                sw_direction = sw_directions[scr_name]
                self.switch_to(
                    av_screens[scr_name],
                    direction=sw_direction,
                )

            else:
                self.switch_to(
                    av_screens[scr_name]
                )


class ImageGalleryApp(App):

    screen_manager = ScrManager()

    def build(self):
        paths = scan_path_for_images('./test-imgs')

        gallery_view = GalleryView(name='gallery')
        gallery_view.paths = paths

        self.screen_manager.add_widget(gallery_view)

        self.screen_manager.add_widget(FullScreenView(name='full_screen'))

        return self.screen_manager


if __name__ == '__main__':
    ImageGalleryApp().run()
