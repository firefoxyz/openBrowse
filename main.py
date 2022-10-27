# importing required libraries
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
# from pypac import PACSession, get_pac
# import shutil
# import requests
# import os
import configparser
import sys
# main window

config = configparser.ConfigParser()
config.read_file(open("resources/config//config.cfg"))
SearchEngine = config.get('User Settings', 'SearchEngine')
DarkMode = config.get('User Settings', 'DarkMode')


class MainWindow(QMainWindow):

	# constructor
	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)

		# creating a tab widget
		self.tabs = QTabWidget()
		self.tabs.setStyleSheet("""
		background-color: rgb(74, 74, 74);
		border-width: 0px;
		""")

		# making document mode true
		self.tabs.setDocumentMode(True)

		# adding action when double click
		self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)

		# adding action when tab is changed
		self.tabs.currentChanged.connect(self.current_tab_changed)

		# making tabs closeable
		self.tabs.setTabsClosable(True)

		# adding action when tab close is requested
		self.tabs.tabCloseRequested.connect(self.close_current_tab)

		# making tabs as central widget
		self.setCentralWidget(self.tabs)

		# creating a status bar
		self.status = QStatusBar()

		# setting status bar to the main window
		self.setStatusBar(self.status)

		# creating a toolbar for navigation
		navbar = QToolBar("Navigation")
		navbar.setIconSize(QSize(16, 16))
		if DarkMode:
			navbar.setStyleSheet("""
			background-color: rgb(74, 74, 74);
			border-width: 0px;
			font: bold 14px;
			padding: 6px;
			""")

		# adding toolbar to the main window
		self.addToolBar(navbar)

		# creating back action
		back_btn = QAction(QIcon("resources/icons//back-icon.png"), "Back", self)

		# setting status tip
		back_btn.setStatusTip("Back to previous page")

		# adding action to back button
		# making current tab to go back
		back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())

		# adding this to the navigation toolbar
		navbar.addAction(back_btn)

		# adding the next button
		next_btn = QAction(QIcon("resources/icons//forward-icon.png"), "Forward", self)
		next_btn.setStatusTip("Forward to next page")
		next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
		navbar.addAction(next_btn)

		# adding the reload button
		reload_btn = QAction(QIcon("resources/icons//refresh-icon.png"), "Reload", self)
		reload_btn.setStatusTip("Reload page")
		reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
		navbar.addAction(reload_btn)

		# new tab button
		new_tab_btn = QAction(QIcon("resources/icons//new-tab-icon.png"), "New Tab", self)
		new_tab_btn.setStatusTip("New Tab")
		new_tab_btn.triggered.connect(lambda: self.add_new_tab())
		navbar.addAction(new_tab_btn)

		# creating home action
		home_btn = QAction(QIcon("resources/icons//home-icon.png"), "Home", self)
		home_btn.setStatusTip("Go home")

		# adding action to home button
		home_btn.triggered.connect(self.navigate_home)
		navbar.addAction(home_btn)

		# adding a separator
		navbar.addSeparator()

		# creating a line edit widget for URL
		self.url_bar = QLineEdit()
		if DarkMode:
			self.url_bar.setStyleSheet("""
			background-color: gray;
			border-width: 0px;
			border-radius: 10px;
			font: italic 12px;
			padding: 6px;
			""")

		# adding action to line edit when return key is pressed
		self.url_bar.returnPressed.connect(self.navigate_to_url)

		# adding line edit to toolbar
		navbar.addWidget(self.url_bar)

		# adding the stop action
		stop_btn = QAction(QIcon("resources/icons//stop-icon.png"), "Stop", self)
		stop_btn.setStatusTip("Stop loading current page")
		stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
		navbar.addAction(stop_btn)

		# creating first tab
		self.add_new_tab(QUrl(SearchEngine), 'Homepage')

		# showing all the components
		self.show()

		# setting window title
		self.setWindowTitle(" - openBrowse 0.3")

	# method for adding new tab
	def add_new_tab(self, qurl=None, label="Blank"):

		# if url is blank
		if qurl is None:
			# creating a new url
			qurl = QUrl(SearchEngine)

		# creating a QWebEngineView object
		browser = QWebEngineView()

		# setting url to browser
		browser.setUrl(qurl)

		# setting tab index
		i = self.tabs.addTab(browser, label)
		self.tabs.setCurrentIndex(i)

		# adding action to the browser when url is changed
		# update the url
		browser.urlChanged.connect(lambda qurl, browser=browser:
								self.update_url_bar(qurl, browser))

		# adding action to the browser when loading is finished
		# set the tab title
		browser.loadFinished.connect(lambda _, i=i, browser=browser:
								self.tabs.setTabText(i, browser.page().title()))

	# when clicked is pressed on tabs
	def tab_open_doubleclick(self, i):

		# checking index i.e
		# No tab under the click
		if i == -1:
			# creating a new tab
			self.add_new_tab()

	# when tab is changed
	def current_tab_changed(self, i):

		# get the curl
		qurl = self.tabs.currentWidget().url()

		# update the url
		self.update_url_bar(qurl, self.tabs.currentWidget())

		# update the title
		self.update_title(self.tabs.currentWidget())

	# when tab is closed
	def close_current_tab(self, i):

		# if there is only one tab
		if self.tabs.count() < 2:
			# do nothing
			return

		# else remove the tab
		self.tabs.removeTab(i)

	# method for updating the title
	def update_title(self, browser):

		# if signal is not from the current tab
		if browser != self.tabs.currentWidget():
			# do nothing
			return

		# get the page title
		title = self.tabs.currentWidget().page().title()

		# set the window title
		self.setWindowTitle("% s openBrowse 0.3" % title)

	# action to go home
	def navigate_home(self):

		# go to google
		self.tabs.currentWidget().setUrl(QUrl(SearchEngine))

	# method for navigate to url
	def navigate_to_url(self):

		# get the line edit text
		# convert it to QUrl object
		q = QUrl(self.url_bar.text())

		# if scheme is blank
		if q.scheme() == "":
			# set scheme
			q.setScheme("http")

		# set the url
		self.tabs.currentWidget().setUrl(q)

	# method to update the url
	def update_url_bar(self, q, browser=None):

		# If this signal is not from the current tab, ignore
		if browser != self.tabs.currentWidget():

			return

		# set text to the url bar
		self.url_bar.setText(q.toString())

		# set cursor position
		self.url_bar.setCursorPosition(0)


# creating a PyQt5 application
app = QApplication(sys.argv)

# setting name to the application
app.setStyleSheet("background-color: black;")
app.setApplicationName("openBrowse 0.3")
app.setApplicationVersion("0.3, the tab update")
app.setWindowIcon(QIcon("resources/icons//window-icon.png"))
# creating MainWindow object
window = MainWindow()

# loop
app.exec_()
