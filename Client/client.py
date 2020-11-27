import requests
import pandas as pd
import gi
import json
from wordcloud import WordCloud

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk, Gio, WebKit2


class Window(Gtk.Window):
      def __init__(self):
            Gtk.Window.__init__(self)
            self.set_default_size(1920, 1080)

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
                  
      def _wordcloud_gen(self, row):
            freq = {key: val for key, val in json.loads(row.wordcloud)}
            wc = WordCloud().generate_from_frequencies(freq)
            wc.to_file('data/' + str(row.id) + '.jpg')
            
      def _load_categories(self, button):
            response = requests.get('http://localhost:5000/categories', params={'source_urls': json.dumps(sources)})
            self.categories = pd.read_json(response.text, orient='split')
            self.categories['id'] = self.categories.index
            self.categories[['id', 'wordcloud']].apply(self._wordcloud_gen, axis=1)            

            # get categories 
            self._clear_container(self.categories_view)
            self.category_dict = dict()
            for i, row in self.categories.iterrows():
                  image = Gtk.Image.new_from_file('data/' + str(i) + '.jpg')
                  button = Gtk.Button()
                  button.add(image)
                  self.category_dict[button] = i
                  self.categories_view.attach(button, i%5, int(i/5), 1, 1)
                  button.connect('clicked', self._load_articles)
                  
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
            category_id = self.category_dict[button]
            article_ids = [int(val) for val in self.categories.at[category_id, 'article_ids'].split(',')]
            response = requests.get('http://localhost:5000/articles', params={'article_ids': json.dumps(article_ids)})
            articles = pd.read_json(response.text, orient='split')
            
            self._clear_container(self.articles_view)
            
            # get list of articles from api 
            self.articles_dict = dict()
            for i, row in articles.iterrows():
                  button_box = Gtk.Box()
                  image_view = WebKit2.WebView()
                  image_view.load_uri(row.top_image)
                  image_view.set_size_request(400, 200)
                  button_box.pack_start(image_view, False, False, 0)
                  button_box.pack_start(Gtk.Label(label=row.title), True, True, 0)
                  button_box.pack_end(Gtk.Label(label=str(row.date)), False, False, 0)
                  button = Gtk.Button()
                  button.add(button_box)
                  self.articles_view.pack_start(button, False, False, 0)
                  button.connect('clicked', self._load_article_url)
                  self.articles_dict[button] = row.url
            
            self._clear_container(self.scrolled_window)
            self.scrolled_window.add(self.articles_view)
            self.articles_view.set_visible(True)
            self.show_all()
            
      def _load_article_url(self, button):
            self.web_view.load_uri(self.articles_dict[button])            
            self.remove(self.scrolled_window)   
            self.add(self.web_view)
            self.web_view.set_visible(True)
            self.show_all()
            

with open('sources.json') as f:
      sources = json.load(f)
      
win = Window()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
