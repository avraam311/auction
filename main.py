import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.popup import Popup


class Auction:
    def __init__(self, title, description, starting_bid):
        self.title = title
        self.description = description
        self.starting_bid = float(starting_bid)
        self.bids = []
        self.timer_event = None

    def place_bid(self, amount):
        if amount > self.starting_bid:
            self.bids.append(amount)
            self.starting_bid = amount
            return True
        return False

    def start_timer(self, callback):
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_once(callback, 15)


class MainPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.auction_list = GridLayout(cols=1, size_hint_y=None)
        self.auction_list.bind(minimum_height=self.auction_list.setter('height'))

        self.load_auctions()

        self.layout.add_widget(self.auction_list)
        self.create_auction_button = Button(text='Создать аукцион', size_hint_y=None, height=50)
        self.create_auction_button.bind(on_press=self.go_to_create_auction)
        self.layout.add_widget(self.create_auction_button)

        self.add_widget(self.layout)

    def load_auctions(self):
        try:
            with open('data/auctions.json', 'r') as f:
                auctions_data = json.load(f)
                for item in auctions_data:
                    auction = Auction(item["Название"], item["Описание"], item["Начальная ставка"])
                    auction_button = Button(text=auction.title, size_hint_y=None, height=40)
                    auction_button.bind(on_press=lambda btn, a=auction: self.go_to_auction_info(a))
                    self.auction_list.add_widget(auction_button)
        except FileNotFoundError:
            pass

    def go_to_create_auction(self, instance):
        self.manager.current = 'create_auction'

    def go_to_auction_info(self, auction):
        self.manager.current = 'auction_info'
        self.manager.get_screen('auction_info').display_auction(auction)

    def add_auction_to_list(self, auction):
        auction_button = Button(text=auction.title, size_hint_y=None, height=40)
        auction_button.bind(on_press=lambda btn, a=auction: self.go_to_auction_info(a))
        self.auction_list.add_widget(auction_button)


class CreateAuctionPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.title_input = TextInput(hint_text="Название аукциона", size_hint_y=None, height=40)
        self.layout.add_widget(self.title_input)

        self.description_input = TextInput(hint_text="Описание аукциона", size_hint_y=None, height=80)
        self.layout.add_widget(self.description_input)

        self.starting_bid_input = TextInput(hint_text="Начальная ставка", size_hint_y=None, height=40)
        self.layout.add_widget(self.starting_bid_input)

        self.create_button = Button(text='Создать аукцион', size_hint_y=None, height=50)
        self.create_button.bind(on_press=self.create_auction)
        self.layout.add_widget(self.create_button)

        self.add_widget(self.layout)

    def create_auction(self, instance):
        title = self.title_input.text
        description = self.description_input.text
        starting_bid = self.starting_bid_input.text

        if title and description and starting_bid:
            auction = Auction(title, description, starting_bid)
            self.save_auction(auction)
            app = App.get_running_app()
            app.root.get_screen('main').add_auction_to_list(auction)
            popup = Popup(title="Успешно", content=Label(text="Аукцион создан!"), size_hint=(0.6, 0.4))
            popup.open()
            self.title_input.text = ''
            self.description_input.text = ''
            self.starting_bid_input.text = ''
            self.manager.current = 'main'
        else:
            popup = Popup(title="Ошибка", content=Label(text="Пожалуйста, заполните все поля"), size_hint=(0.6, 0.4))
            popup.open()

    def save_auction(self, auction):
        try:
            with open('data/auctions.json', 'r') as f:
                auctions_data = json.load(f)
        except FileNotFoundError:
            auctions_data = []

        auctions_data.append(
            {"Название": auction.title, "Описание": auction.description, "Начальная ставка": auction.starting_bid})

        with open('data/auctions.json', 'w') as f:
            json.dump(auctions_data, f)


class AuctionInfoPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.title_label = Label(size_hint_y=None, height=40)
        self.description_label = Label(size_hint_y=None, height=80)
        self.starting_bid_label = Label(size_hint_y=None, height=40)

        self.bid_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.bid_input = TextInput(hint_text="Ваша ставка", size_hint_x=0.7)
        self.bid_button = Button(text="Сделать ставку", size_hint_x=0.3)
        self.bid_button.bind(on_press=self.place_bid)

        self.bid_layout.add_widget(self.bid_input)
        self.bid_layout.add_widget(self.bid_button)

        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.description_label)
        self.layout.add_widget(self.starting_bid_label)
        self.layout.add_widget(self.bid_layout)

        back_button = Button(text="Вернуться к аукционам", size_hint_y=None, height=50)
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)

        self.result_label = Label(size_hint_y=None, height=40)
        self.layout.add_widget(self.result_label)

        self.add_widget(self.layout)

    def display_auction(self, auction):
        self.auction = auction
        self.title_label.text = f'Название: {auction.title}'
        self.description_label.text = f'Описание: {auction.description}'
        self.starting_bid_label.text = f'Начальная ставка: ${auction.starting_bid: .2f}'

        self.result_label.text = ''

    def place_bid(self, instance):
        bid_amount_str = self.bid_input.text
        if bid_amount_str:
            try:
                bid_amount = float(bid_amount_str)
                if self.auction.place_bid(bid_amount):
                    popup = Popup(title="Успешно", content=Label(text=f'Ставка размером в ${bid_amount: .2f} сделана! \n'
                                                                      f'Если в течение 15 секунд никто не перебьет \n'
                                                                      f'вашу ставку, вы выиграете!'),
                                  size_hint=(0.6, 0.4))
                    popup.open()
                    self.starting_bid_label.text = f'Начальная ставка: ${self.auction.starting_bid: .2f}'

                    self.auction.start_timer(lambda dt: self.end_auction())

                    self.bid_input.disabled = True
                    self.bid_button.disabled = True
                else:
                    popup = Popup(title="Ошибка",
                                  content=Label(text='Нужно сделать ставку выше текущей.'),
                                  size_hint=(0.6, 0.4))
                    popup.open()
            except ValueError:
                popup = Popup(title="Ошибка", content=Label(text='Введите валидное число.'), size_hint=(0.6, 0.4))
                popup.open()

    def end_auction(self):
        if self.auction.bids:
            winning_bid = max(self.auction.bids)
            winning_bid_text = f'Выигрышная ставка: ${winning_bid: .2f}'
            print(f"Аукцион '{self.auction.title}' окончен. Выигрышная ставка: ${winning_bid: .2f}")
            self.result_label.text = f'Аукцион закрыт! {winning_bid_text}'
            self.bid_input.disabled = True
            self.bid_button.disabled = True
        else:
            print(f"Аукцион '{self.auction.title}' закончился без ставок.")
            self.result_label.text = 'Аукцион закрыт. Ставок не было.'

    def go_back(self, instance):
        self.manager.current = 'main'


class AuctionApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainPage(name='main'))
        sm.add_widget(CreateAuctionPage(name='create_auction'))
        sm.add_widget(AuctionInfoPage(name='auction_info'))

        return sm


if __name__ == '__main__':
    AuctionApp().run()
