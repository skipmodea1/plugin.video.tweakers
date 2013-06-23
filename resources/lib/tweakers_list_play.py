#
# Imports
#
from BeautifulSoup import BeautifulSoup
from tweakers_const import __addon__, __settings__, __language__, __images_path__, __date__, __version__
from tweakers_utils import HTTPCommunicator
import os
import re
import sys
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

#
# Main class
#
class Main:
	#
	# Init
	#
	def __init__( self ) :
		# Get plugin settings
		self.DEBUG     = __settings__.getSetting('debug')
		
		if (self.DEBUG) == 'true':
			xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s, %s = %s" % ( __addon__, __version__, __date__, "ARGV", repr(sys.argv), "File", str(__file__) ), xbmc.LOGNOTICE )

		# Parse parameters...
		if len(sys.argv[2]) == 0:
			self.plugin_category = __language__(30000)
			self.video_list_page_url = "http://tweakers.net/video/zoeken/?page=001"
			self.next_page_possible = True
		else:
			self.plugin_category = urlparse.parse_qs(urlparse.urlparse(sys.argv[2]).query)['plugin_category'][0]
			self.video_list_page_url = urlparse.parse_qs(urlparse.urlparse(sys.argv[2]).query)['url'][0]
			self.next_page_possible = urlparse.parse_qs(urlparse.urlparse(sys.argv[2]).query)['next_page_possible'][0]

		if (self.DEBUG) == 'true':
			xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "self.video_list_page_url", str(self.video_list_page_url) ), xbmc.LOGNOTICE )
		
		if self.next_page_possible == 'True':
		# Determine current item number, next item number, next_url
		#f.e. http://www.gamekings.tv/category/videos/page/001/
			pos_of_page		 			 	 = self.video_list_page_url.rfind('?page=')
			if pos_of_page >= 0:
				page_number_str			     = str(self.video_list_page_url[pos_of_page + len('?page='):pos_of_page + len('?page=') + len('000')])
				page_number					 = int(page_number_str)
				page_number_next			 = page_number + 1
				if page_number_next >= 100:
					page_number_next_str = str(page_number_next)
				elif page_number_next >= 10:
					page_number_next_str = '0' + str(page_number_next)
				else:				
					page_number_next_str = '00' + str(page_number_next)
				self.next_url = str(self.video_list_page_url).replace(page_number_str, page_number_next_str)
			
				if (self.DEBUG) == 'true':
					xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "self.next_url", str(urllib.unquote_plus(self.next_url)) ), xbmc.LOGNOTICE )
	
		#
		# Get the videos...
		#
		self.getVideos()
	
	#
	# Get videos...
	#
	def getVideos( self ) :
		#
		# Init
		#
		titles_index = 0
		thumbnail_url = ''
		self.next_url = ''
		
		# 
		# Get HTML page...
		#
		html_source = HTTPCommunicator().get( self.video_list_page_url )

		# Parse response...
		soup = BeautifulSoup(html_source)

		# Get titles
		#<a href="http://tweakers.net/video/7515/karma-the-enlightened-one-uit-league-of-legends.html" class="thumb video" title="Karma the Enlightened One uit League of Legends">
        thumbnail_urls = soup.findAll('a', attrs={'title'})
        
		if (self.DEBUG) == 'true':
			xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "len(titles)", str(len(titles)) ), xbmc.LOGNOTICE )

		# Get video-page-urls
		#<a href="http://tweakers.net/video/7515/karma-the-enlightened-one-uit-league-of-legends.html" class="thumb video" title="Karma the Enlightened One uit League of Legends">
				thumbnail_urls = soup.findAll('img', attrs={'src': re.compile("^http://www.gamekings.tv/wp-content/uploads/")})
		video_page_urls = soup.findAll('enclosure')
		
		if (self.DEBUG) == 'true':
			xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "len(video_page_urls)", str(len(video_page_urls)) ), xbmc.LOGNOTICE )
		
		for video_page_url in video_page_urls:
			video_page_url = str(video_page_url['url'])
					
			# Make title					
			#<guid>http://nl.hardware.info/tv/569/winnaar-rog-my-pc-upgrade-actie</guid>
			title = str(titles[titles_index])
			#remove the trailing </guid>'
			title = title[0:len(title) - len('<guid>') - 1]
			pos_of_last_slash = title.rfind('/')
			title = title[pos_of_last_slash + 1:]
			title = title.capitalize()
			title = title.replace('-',' ')
			title = title.replace('/',' ')
			title = title.replace('_',' ')		
					
			if (self.DEBUG) == 'true':
				xbmc.log( "[ADDON] %s v%s (%s) debug mode, %s = %s" % ( __addon__, __version__, __date__, "title", str(title) ), xbmc.LOGNOTICE )
							
			# Add to list...
			listitem        = xbmcgui.ListItem( title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail_url )
			listitem.setInfo( "video", { "Title" : title, "Studio" : "tweakers" } )
			listitem.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem( handle=int(sys.argv[ 1 ]), url=video_page_url, listitem=listitem, isFolder=False)
				
			titles_index = titles_index + 1
		
		#Next page entry, not possible yet...
		if self.next_page_possible == 'True':
			parameters = {"action" : "list-play", "plugin_category" : self.plugin_category, "url" : str(self.next_url), "next_page_possible": self.next_page_possible}
			url = sys.argv[0] + '?' + urllib.urlencode(parameters)
			listitem = xbmcgui.ListItem (__language__(30503), iconImage = "DefaultFolder.png", thumbnailImage = os.path.join(__images_path__, 'next-page.png'))
			folder = True
			xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ] ), url = url, listitem=listitem, isFolder=folder)

		# Disable sorting...
		xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
		
		# End of directory...
		xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )
