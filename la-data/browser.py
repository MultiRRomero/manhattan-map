import mechanize

def get_browser():
  br = mechanize.Browser()
  br.set_cookiejar(mechanize.CookieJar())
  
  br.set_handle_equiv(True)
  br.set_handle_redirect(True)
  br.set_handle_referer(True)
  br.set_handle_robots(False)
  
  br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
  br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
  return br

def open_page(br, url):
  resp = br.open(url)
  s = resp.read()
  resp.close()
  return s.decode('utf-8', 'replace').encode('ascii', 'replace')
