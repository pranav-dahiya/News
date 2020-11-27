import requests
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk, Gio, WebKit2


class Window(Gtk.Window):
      def __init__(self):
            Gtk.Window.__init__(self)
            self.set_default_size(800, 800)

            hb = Gtk.HeaderBar()
            hb.set_show_close_button(True)
            hb.props.title = "News"
            self.set_titlebar(hb)

            button = Gtk.Button()
            button.connect('clicked', self._load_categories)
            icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(image)
            hb.pack_end(button)

            button = Gtk.Button()
            button.connect('clicked', self._back)
            button.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.LEFT, shadow_type=Gtk.ShadowType.NONE))
            hb.pack_start(button)
            
            self.scrolled_window = Gtk.ScrolledWindow()
            self.add(self.scrolled_window)
            
            self.categories_view = Gtk.Grid()
            self.scrolled_window.add(self.categories_view)
            
            self.articles_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            
            self.web_view = WebKit2.WebView()
            
            self._load_categories(None)
            
      def _clear_container(self, container):
            for widget in container.get_children():
                  widget.set_visible(False)
                  container.remove(widget)
            
      def _load_categories(self, button):
            print('load categories from api')
            
            # get categories 
            self._clear_container(self.categories_view)
            categories = range(100)
            self.category_dict = dict()
            for i, button in enumerate(map(lambda i: Gtk.Button.new_with_label(str(i)), categories)):
                  self.categories_view.attach(button, i%5, int(i/5), 1, 1)
                  button.connect('clicked', self._load_articles)
                  self.category_dict[button] = i
                  
            if self.web_view in self.get_children():
                  self.remove(self.web_view)
                  self.add(self.scrolled_window)
                  self.web_view.set_visible(False)
            self._clear_container(self.scrolled_window)
            self.scrolled_window.add(self.categories_view)
            self.categories_view.set_visible(True)
            self.show_all()
            
      def _back(self, button):
            if self.web_view.is_visible():
                  self.remove(self.web_view)
                  self.add(self.scrolled_window)
                  self.web_view.set_visible(False)
                  self.articles_view.set_visible(True)
            elif self.articles_view.is_visible():
                  self._clear_container(self.scrolled_window)
                  self.scrolled_window.add(self.categories_view)
                  self.articles_view.set_visible(False)
                  self.categories_view.set_visible(True)
            self.show_all()
             
      def _load_articles(self, button):
            print('load articles from category', self.category_dict[button])
            self._clear_container(self.articles_view)
            
            # get list of articles from api 
            articles = range(100)
            self.articles_dict = dict()
            for i in articles:
                  button_box = Gtk.Box()
                  image_view = WebKit2.WebView()
                  image_view.load_uri('https://image.cnbcfm.com/api/v1/image/106577930-1592223377872gettyimages-1169040174.jpeg?v=1592223431')
                  image_view.set_size_request(100, 50)
                  button_box.pack_start(image_view, False, False, 0)
                  button_box.pack_start(Gtk.Label(label='Title of article ' + str(i)), True, True, 0)
                  button_box.pack_end(Gtk.Label(label='25/11/2020'), False, False, 0)
                  button = Gtk.Button()
                  button.add(button_box)
                  self.articles_view.pack_start(button, False, False, 0)
                  button.connect('clicked', self._load_article_url)
                  self.articles_dict[button] = i
            
            self._clear_container(self.scrolled_window)
            self.scrolled_window.add(self.articles_view)
            self.articles_view.set_visible(True)
            self.show_all()
            
      def _load_article_url(self, button):
            url = self.articles_dict[button]
            print('article', url)
            self.web_view.load_uri('https://cnn.com')            
            self.remove(self.scrolled_window)   
            self.add(self.web_view)
            self.web_view.set_visible(True)
            self.show_all()
      
win = Window()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
