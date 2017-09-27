from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.proxy import *
import json, ast, sys, requests, urllib,csv, os, shutil, time, glob
import sys, requests, urllib,MySQLdb,time,datetime
from api import AmazonAPI
from tendo import singleton
import httplib, collections
from base64 import b64encode
from logtocloud import *
from checkmarginprice import *
from utility import *
from ordercsv import *
from ResolveCaptcha import ResolveCaptcha
import deathbycaptcha
reload(sys)
sys.setdefaultencoding('utf8')

def loginaccount(browser,checkflag,sellerid):
    amzSql = "select username,password from amazon_account where id='28'"
    print "loginac called"  #testing
    cursor.execute(amzSql)
    acc = cursor.fetchone()
    #print acc
    userName = acc[0]
    passWord = acc[1].decode('base64')
    username = browser.find_element_by_id('ap_email')
    username.send_keys(userName)
    time.sleep(1)
    passwd = browser.find_element_by_id('ap_password')
    passwd.send_keys(passWord)
    try:
        browser.find_element_by_id('signInSubmit-input').click()
    except:    
        browser.find_element_by_id('signInSubmit').click()
    time.sleep(15)
    if checkflag == 1:
        return
    
    ## Captcha Handling 
    itr = 1
    passflag = 0
	
    if 'invalid email' in browser.page_source:
        username.send_keys(userName)
        time.sleep(1)
        passwd.send_keys(passWord)        	
        passwd.send_keys(Keys.RETURN)
        time.sleep(15)
        if 'Sign In' not in browser.title:
		    return
 
    while (itr <= 1):
		try:
			capchadata = browser.find_element_by_id('auth-captcha-image')
			captchaurl = capchadata.get_attribute('src')
			print "CaptchaURL -",captchaurl
			try:
                
				urllib.urlretrieve(str(captchaurl),"capcha_img.png")
				captchatext = ResolveCaptcha("capcha_img.png")
				print "CaptchaText -",captchatext
			except Exception as err1:
				print "Iteration - %s: Failed to get Captcha text" %str(itr)
				itr += 1
				time.sleep(5)
				continue
			try:
				passwd = browser.find_element_by_id('ap_password')
				passwd.send_keys(passWord)
				time.sleep(2)
				capchaval = browser.find_element_by_id('auth-captcha-guess')
				for curval in str(captchatext).strip():
					capchaval.send_keys(curval)
					time.sleep(0.3)
				try:
					browser.find_element_by_id('signInSubmit-input').click()
				except:    
					browser.find_element_by_id('signInSubmit').click()
				time.sleep(10)
				if str(browser.title) != "Amazon Sign In":
					passflag = 1
					break
			except Exception as err2:
				print "Err2 -",err2
				print "Iteration - %s: Failed to Login Amazon using Captcha text" %str(itr)
				itr += 1
				time.sleep(5)
				continue
            
			if itr == 2:
				break
			itr += 1
			time.sleep(5)
		except Exception as err3:
			passflag = 1
			break
    
    if itr > 2 and passflag == 0:
        subject = "Failed to Login Amazon in 3 attempts with captcha text"
        message = "Failed to Login Amazon in 3 attempts and please check manually.Hence exiting from the script"
        Status = SendMail(subject, message)
        if Status:
            print "Failed to Login Amazon Email Sent Successfully"
        else:
            print "Failed to Login Amazon, Failed to send email.Please check for Email settings"
        
        ManualCheck(browser)
        return		
    else:
        #print "Sucessfully Login to Amazon Account"
        time.sleep(100)
        pass
        return		
    '''
    if "Manage Address Book" in browser.title:
        subject = "Failed to open Amazon Home URL"
        message = "Please check for Amazon Username and Password. Problem may also be due to Captcha issue."
        Status = SendMail(subject, message)
        if Status:
            logMessageToCloud(loggroup,logstream, "Email Sent Successfully")
            #browser.quit()
            #sys.exit(0)
        else:
            logMessageToCloud(loggroup,logstream, "Failed to send email.Please check for Email settings")
            #browser.quit()
            #sys.exit(0)
        ManualCheck(browser)
    '''

def getTopcashbackLink(browser):
    try:
        browser.get('https://www.topcashback.com/earncashback.aspx?mpurl=amazon&moid=35428')
        time.sleep(3)
        
        amzSql2 = "select username,password from topcashback"
        cursor.execute(amzSql2)
        acc = cursor.fetchone()
        #print accf
        userName = acc[0]
        passWord = acc[1].decode('base64')
        
        browser.find_element_by_id('ctl00_GeckoOneColPrimary_LoginV2_txtEmail').send_keys(userName)
        #browser.find_element_by_id('ctl00_GeckoOneColPrimary_LoginV2_txtEmail').send_keys("james87778@gmail.com")
        browser.find_element_by_id('ctl00_GeckoOneColPrimary_LoginV2_txtPassword').send_keys(passWord)
        #browser.find_element_by_id('ctl00_GeckoOneColPrimary_LoginV2_txtPassword').send_keys("YomTov78")
        time.sleep(2)
        
        
        browser.find_element_by_id('ctl00_GeckoOneColPrimary_LoginV2_Loginbtn').click()
        time.sleep(10)
    except NoSuchElementException:
        return "Fail"
        '''
        subject = "Failed to find Elements for Topcashback URL Page"
        message = "We failed to find elements for Topcashback URL Page. Please check manually to confirm the issue"
        Status = SendMail(subject, message)
        if Status:
            print "Email Sent Successfully"
            browser.quit()
            sys.exit(0)
        else:
            print "Failed to send email.Please check for Email settings"
            browser.quit()
            sys.exit(0)
        '''
    if not 'amazon.com' in browser.current_url:
        time.sleep(4)
    if 'amazon.com' in browser.current_url:
        param = browser.current_url.split('?')
        return param[1]
    else:
        return "Fail"
        '''
        subject = "Failed to open Topcashback URL"
        message = "Please check for Topcashback Username and Password. Problem may also be due to Captcha issue."
        Status = SendMail(subject, message)
        if Status:
            print "Email Sent Successfully"
            browser.quit()
            sys.exit(0)
        else:
            print "Failed to send email.Please check for Email settings"
            browser.quit()
            sys.exit(0)
        '''

def AddGiftMessage(browser,msg="Thank You"):
    browser.find_element_by_xpath("//a[@class='a-button-text checkout-giftbox-icon']").click()
    time.sleep(3)
    browser.find_element_by_name("gift-message-text").clear()
    time.sleep(2)
    browser.find_element_by_name("gift-message-text").send_keys(msg)
    time.sleep(3)
    browser.find_element_by_xpath(".//*[@id='a-popover-content-2']/div/div/ol/li[3]/span/span[2]/span/input").click()
    time.sleep(3)

## Return Gift Card Balance in Dollars
def GetGiftCardBalance(browser):
    #giftbal = browser.find_element_by_xpath(".//*[@id='your-balances-section']/div[2]/div/div[2]/label/span/span[1]/span").text
    giftbal = browser.find_element_by_xpath(".//label[@class='balance-checkbox']/span[2]/strong").text
    time.sleep(2)
    logMessageToCloud(loggroup,logstream, "Gift Card Balance -" + str(giftbal))
    reobj = re.search(r"\$(.*) of your \$(.*) gift card balance",giftbal,re.I)
    if reobj:
        actualbal = reobj.group(1).strip()
        actualbal = actualbal.split(",")
        actualval = float(''.join(actualbal))
        availbal = reobj.group(2).strip()
        availbal = availbal.split(",")
        mainbal = float(''.join(availbal))
        giftbalval = float(mainbal) - float(actualval)
        balval = "$"+ str(giftbalval)
        return balval
    return None

## Function to delete old Address
def DeleteAMZAddress(browser,addressname,sellerid):
    browser.get('https://www.amazon.com/a/addresses?ref=ya_address_book_add_to_address_book_breadcrumb')
    time.sleep(4)
    print "deleteaddress"  #testing
    try:
        browser.find_element_by_id('ap_email')
        loginaccount(browser,0,sellerid)
    except:
        pass
    ## Get Address List
    while True:
        addrlst = GetAMZAddressList(browser)
        if len(addrlst) == 0:
            break
        if len(addrlst) == 1:
            logMessageToCloud(loggroup,logstream, "No old Addresses to delete")
            break

        addrflag = 0
        for curnameval in addrlst:
            if curnameval == addressname.strip():
                addrflag += 1
                continue
            #print "Going to delete address :",curnameval
            try:
                browser.find_element_by_xpath(".//*[@id='ya-myab-address-delete-btn-%s']/span" %(str(addrflag))).click()
                time.sleep(2)
                browser.find_element_by_xpath(".//*[@id='deleteAddressModal-%s-submit-btn']/span/input" %(str(addrflag))).click()
            except NoSuchElementException:
                logMessageToCloud(loggroup,logstream, "Failed to delete Address containing Full Name :" + str(curnameval))
                pass
            addrflag += 1
            logMessageToCloud(loggroup,logstream, "Successfully deleted Address containing Full Name :" + curnameval)
            time.sleep(2)
            break

## Function to get Address List
def GetAMZAddressList(browser):
    try:
        addrnames = browser.find_elements_by_xpath(".//*[@id='address-ui-widgets-FullName']")
    except NoSuchElementException:
        logMessageToCloud(loggroup,logstream, "Failed to get Address Full Name List")
        pass
    addrlst = []
    for curname in addrnames:
        if curname.text == '':
            continue
        addrlst.append(curname.text)

    return addrlst

## Function to Check Address matching
def MatchAddress(browser,itemlen,address,ordersno,mainqty):

    matchlst = []
    for curindex in range(1, itemlen + 1):
        
        try:
            
            asinelem = browser.find_element_by_xpath(".//*[@id='spc-orders']/div[%s]/div/div[4]/div/div/div[2]/div[1]/input" %(str(curindex)))
            
            asindata = asinelem.get_attribute('value')
            #print "Asindata =",asindata
            
            tempval = asindata.split("|")
            asinvalue = tempval[0]
            #print "Asin value =",asinvalue
            
            #print "Address value =",address[asinvalue]
            
            #print "Address Name =",address[asinvalue]['name']
            #print "Address Addr1 =",address[asinvalue]['add1']
            
            getaddrvalue = browser.find_element_by_xpath(".//*[@id='spc-orders']/div[%s]/div/div[3]" %(str(curindex))).text
            #print "GetAddress =",getaddrvalue
            
            addrobj = re.search("Shipping address:(.*)",getaddrvalue)
            if addrobj:
				addrdata1 = addrobj.group(1).strip()
				addrdata2 = addrdata1.split(",")
				logMessageToCloud(loggroup,logstream, addrdata2[0].strip())
				logMessageToCloud(loggroup,logstream, addrdata2[1].strip())
				addrname = address[asinvalue]['name']
				addrname = addrname.split(",")
				if str(addrname[0].strip()) == str(addrdata2[0].strip()):
					logMessageToCloud(loggroup,logstream, "Address matched : " + address[asinvalue]['name'])
				else:
					logMessageToCloud(loggroup,logstream, "Address not matched :" + address[asinvalue]['name'])
					matchlst.append(asinvalue)
                    
            else:
                logMessageToCloud(loggroup,logstream, "Not able to get address for Asin value -" + asinvalue)
        except Exception as err:
            logMessageToCloud(loggroup,logstream, "Error: Cannot match Addresses." + str(err))

    if len(matchlst) > 0:
        browser.find_element_by_xpath(".//*[@id='spc-orders']/div[1]/div/div[3]/a").click()
    
    for key in matchlst:
        SelectMultipleAddress(browser,address,inputasin=key)
        subject = "Deleted Item with asin value %s" %(str(key))
        message = "We have sucessfully deleted item with asin value %s as address selected not matched with main address dictionary" %(str(key))
        Status = SendMail(subject, message)
        if Status:
            logMessageToCloud(loggroup,logstream, "Email Sent Successfully")
        else:
            logMessageToCloud(loggroup,logstream, "Failed to send email.Please check for Email settings")
            #browser.quit()
            #sys.exit(0)
            
        del address[key]
        del ordersno[key]
        del mainqty[key]
        time.sleep(2) 
    if len(matchlst) > 0:
        browser.find_element_by_name("continueMultiAddress").click()
        MatchAddress(browser,itemlen,address,ordersno,mainqty)		
    time.sleep(2)

## Select Multiple Address
def SelectMultipleAddress(browser,address,inputasin=''):
    
    for i in range(1,len(address)+1):
        asinname = 'asin.' + str(i)
            
        deleteasin = 'delete.' + str(i)
        currentASIN =str( browser.find_element_by_name(asinname).get_attribute("value"))
        logMessageToCloud(loggroup,logstream, currentASIN)
        if inputasin != '':
            if inputasin != currentASIN:
                continue
            else:
                deladdr = 'delete.' + str(i)
                browser.find_element_by_name(deladdr).click()
                time.sleep(2)
                logMessageToCloud(loggroup,logstream, "Successfully deleted Asin item from list : " + currentASIN)
                break

## Add Gift Message to item if not exists
def CheckGiftMessage(browser,itemlen):
    
    if itemlen == 1:
        flag = 0
        checkflag = 1
        giftmsgdata = ''
        try:
            giftmsgdata = browser.find_element_by_xpath(".//*[@id='spc-orders']/div/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[5]/div[1]/span/span/a").text
            time.sleep(2)
        except:
            pass
        
        try:
            if giftmsgdata == '':
                giftmsgdata = browser.find_element_by_xpath(".//*[@id='spc-orders']/div/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[6]/div[1]/span/span/a").text
                time.sleep(2)
                checkflag = 2
        except:
            flag = 1
        
        if flag == 0:
            #print "Gift Option -",giftmsgdata.strip()
            if giftmsgdata.strip() == "Add a gift receipt" or giftmsgdata.strip() == "Add gift options":
                try:
                    
                    if checkflag == 1:
                        browser.find_element_by_xpath(".//*[@id='spc-orders']/div/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[5]/div[1]/span/span/a").click()
                    else:
                        browser.find_element_by_xpath(".//*[@id='spc-orders']/div/div/div[3]/div/div/div[2]/div[1]/div/div[2]/div[6]/div[1]/span/span/a").click()
                    time.sleep(2)
                    browser.find_element_by_xpath(".//*[@id='a-popover-1']/div/div[2]/div/div/ol/li[2]/div[2]/div[1]/textarea").clear()
                    
                    browser.find_element_by_xpath(".//*[@id='a-popover-1']/div/div[2]/div/div/ol/li[2]/div[2]/div[1]/textarea").send_keys('Thank You')
                    time.sleep(1)
                    browser.find_element_by_xpath(".//*[@id='a-popover-1']/div/div[2]/div/div/ol/li[3]/span[2]/span/input").click()
                    time.sleep(5)
                    logMessageToCloud(loggroup,logstream, "Successfully Added Gift Message to item")
                    
                except Exception as err:
                    logMessageToCloud(loggroup,logstream, "Failed to Add Gift Message to item."+ str(err))
                    subject = "Failed to Add Gift Message to item"
                    message = "We have failed to Add Gift Message to item.",err
                    Status = SendMail(subject, message)
                    if Status:
                        logMessageToCloud(loggroup,logstream, "Email Sent Successfully")
                    else:
                        logMessageToCloud(loggroup,logstream, "Failed to send email.Please check for Email settings")
                        #browser.quit()
                        #sys.exit(0)
                    ManualCheck(browser)
                    
            
    else:
        
            #print "Current Item len -",itemlen
            for curindex in range(1, itemlen + 1):
                giftmsgdata = ''
                checkflag = 1
                try:
                    giftmsgdata = browser.find_element_by_xpath(".//*[@id='spc-orders']/div[%s]/div/div[4]/div/div/div[2]/div[1]/div/div[2]/div[6]/div[1]/span/span/a" %(str(curindex))).text
                    time.sleep(2)
                except:
                    pass
                
                try:
                    if giftmsgdata == '':
                        giftmsgdata = browser.find_element_by_xpath(".//*[@id='spc-orders']/div[%s]/div/div[4]/div/div/div[2]/div[1]/div/div[2]/div[7]/div[1]/span/span/a" %(str(curindex))).text
                        time.sleep(2)
                        checkflag = 2
                except:
                    continue
                #print "Gift Option -",giftmsgdata.strip()
                if giftmsgdata.strip() == "Add a gift receipt" or giftmsgdata.strip() == "Add gift options":
                    try:
                        if checkflag == 1:
                            browser.find_element_by_xpath(".//*[@id='spc-orders']/div[%s]/div/div[4]/div/div/div[2]/div[1]/div/div[2]/div[6]/div[1]/span/span/a" %(str(curindex))).click()
                        else:
                            browser.find_element_by_xpath(".//*[@id='spc-orders']/div[%s]/div/div[4]/div/div/div[2]/div[1]/div/div[2]/div[7]/div[1]/span/span/a" %(str(curindex))).click()
                        
                        time.sleep(2)
                        try:
                            browser.find_element_by_xpath(".//*[@id='a-popover-%s']/div/div[2]/div/div/ol/li[2]/div[2]/div[1]/textarea" %(str(curindex))).clear()
                            browser.find_element_by_xpath(".//*[@id='a-popover-%s']/div/div[2]/div/div/ol/li[2]/div[2]/div[1]/textarea" %(str(curindex))).send_keys('Thank You')
                            time.sleep(1)
                            browser.find_element_by_xpath(".//*[@id='a-popover-%s']/div/div[2]/div/div/ol/li[3]/span[2]/span/input" %(str(curindex))).click()
                            
                        except:
                            browser.find_element_by_xpath(".//*[@id='a-popover-1']/div/div[2]/div/div/ol/li[2]/div[2]/div[1]/textarea").clear()
                            browser.find_element_by_xpath(".//*[@id='a-popover-1']/div/div[2]/div/div/ol/li[2]/div[2]/div[1]/textarea").send_keys('Thank You')
                            time.sleep(1)
                            browser.find_element_by_xpath(".//*[@id='a-popover-1']/div/div[2]/div/div/ol/li[3]/span[2]/span/input").click()
                        
                        logMessageToCloud(loggroup,logstream, "Successfully Added Gift Message to item %s "   + str(curindex))
                        
                        time.sleep(5)
                        
                    except Exception as err:
                        logMessageToCloud(loggroup,logstream, "Failed to Add Gift Message to item." + str(err))
                        subject = "Failed to Add Gift Message to item %s" %(str(curindex))
                        message = "We have failed to Add Gift Message to item %s. %s" %(str(curindex),str(err))
                        Status = SendMail(subject, message)
                        if Status:
                            logMessageToCloud(loggroup,logstream, "Email Sent Successfully")
                        else:
                            logMessageToCloud(loggroup,logstream, "Failed to send email.Please check for Email settings")
                            #browser.quit()
                            #sys.exit(0)
                        ManualCheck(browser)



def DeleteCartItems(browser):
    
    cartflag = 1
    while True:

        try:
            browser.get('https://www.amazon.com/gp/cart/view.html/ref=nav_bnav_cart')
            time.sleep(3)
        except NoSuchElementException:
            logMessageToCloud(loggroup,logstream, "Failed to enter Cart Menu")
            sys.exit()
        cartlen = GetCartLength(browser)
        if cartlen == 0:
            break
        if cartlen == 1:
            delcart = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div/div[4]/div/div[1]/div/div/div[2]/div/span[1]/span/input")
            delcart.click()
            logMessageToCloud(loggroup,logstream, "Cart Item %s deleted sucessfully"  + str(cartflag))
            break
        else:
            for curitem in range(1,cartlen + 1):
                try:
                    time.sleep(3)
                    delcart = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div[%s]/div[4]/div/div[1]/div/div/div[2]/div/span[1]/span/input" %(str(curitem)))
                    delcart.click()
                except NoSuchElementException:
                    logMessageToCloud(loggroup,logstream, "Failed to delete Cart Item %s"  + str(cartflag))
                    #browser.quit()
                    #sys.exit(0)
                    ManualCheck(browser)
                logMessageToCloud(loggroup,logstream, "Cart Item %s deleted sucessfully"  + str(cartflag))
                cartflag += 1
                time.sleep(2)
                break

## Get Cart Length
def GetCartLength(browser):
    try:
        cartlen = browser.find_elements_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div")
        maincartlen = len(cartlen)
        time.sleep(2)
    except NoSuchElementException:
        return 0
    return maincartlen

    
def placeOrder(link,ordersno,address,orderanywaylst,sellerid,mainqty,cartissueflag,Offers):
    print "Entered Place order method" #testing
    print link, ordersno, address, orderanywaylst, sellerid, mainqty, cartissueflag, Offers #testing
    ## Get Proxy settings data
    proxysql = "SELECT username,password,ip,port FROM `proxy` where id in (select proxy_id from amazon_account where id = '" + str(sellerid) + "')"
    logMessageToCloud(loggroup,logstream, proxysql)
    cursor.execute(proxysql)
    proxydetails = cursor.fetchone()
    if len(proxydetails) > 1:
        usrname = proxydetails[0]
        passwd = proxydetails[1].decode('base64')
        tokendata = '%s:%s' %(str(usrname),str(passwd))
        authtoken = b64encode(tokendata)
        #print authtoken
        ipaddr = proxydetails[2]
        portnum = proxydetails[3]
        profile = webdriver.FirefoxProfile()
        profile.set_preference("signon.autologin.proxy",True)
        profile.add_extension(extension="close_proxy.xpi")
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", str(ipaddr)) #james87778:P95JIEXd
        profile.set_preference("network.proxy.http_port", int(portnum))
        profile.set_preference("network.proxy.ssl", str(ipaddr)) #james87778:P95JIEXd
        profile.set_preference("network.proxy.ssl_port", int(portnum))
        profile.set_preference("extensions.closeproxyauth.authtoken",authtoken)
        profile.update_preferences()
        browser = webdriver.Firefox(firefox_profile=profile)
        
        browser.get("http://www.amazon.com/")
        time.sleep(4)
        if "Amazon" not in browser.title:
            logMessageToCloud(loggroup,logstream, "Proxy settings issue")
            subject = "Failed to open Firefox browser with Proxy Settings"
            message = "Please check for Proxy Username, Password, Port and IPAddress."
            Status = SendMail(subject, message)
            if Status:
                logMessageToCloud(loggroup,logstream, "Proxy Email Sent Successfully")
                browser.quit()
                browser = webdriver.Firefox()
            else:
                logMessageToCloud(loggroup,logstream, "Failed to send email.Please check for Email settings")
                #browser.quit()
                #sys.exit(0)
        #browser = webdriver.Firefox()
    else:
        browser = webdriver.Firefox() #firefox_profile=profile
        
    browser.implicitly_wait(10)
    #browser.get('https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_signin') 
    #getTopUrl = getTopcashbackLink(browser)
    #print getTopUrl
    i = 1
    while (i <= 3):
        getTopUrl = getTopcashbackLink(browser)
        print getTopUrl
        #logMessageToCloud(loggroup,logstream, getTopUrl)
        if str(getTopUrl) != "Fail":
            break
        time.sleep(10)
        i += 1
    #sys.exit(0)
    
    ## Delete Old Addresses before adding new ones
    DeleteAMZAddress(browser,'Gold Deals LLC',sellerid)
    time.sleep(1)
    ## Delete Cart Items
    DeleteCartItems(browser)
    time.sleep(2)
    deleteASINs = []
    for key,add in address.iteritems():
        try:
            browser.get('https://www.amazon.com/gp/css/account/address/view.html?ie=UTF8&ref_=myab_view_new_address_form&viewID=newAddress')
        except:
            time.sleep(3)
            browser.get('https://www.amazon.com/gp/css/account/address/view.html?ie=UTF8&ref_=myab_view_new_address_form&viewID=newAddress')            
        time.sleep(2)
        try:
            browser.find_element_by_id('ap_email')
            loginaccount(browser,0,sellerid)
        except:
            pass
        logMessageToCloud(loggroup,logstream, str(add))
        time.sleep(5)
        
        if 'US' in add['country']:
            try:         
                browser.find_element_by_id('enterAddressFullName').send_keys(add['name'].encode("utf-8"))
                browser.find_element_by_id('enterAddressAddressLine1').send_keys(add['add1'].encode("utf-8"))
                browser.find_element_by_id('enterAddressAddressLine2').send_keys(add['add2'].encode("utf-8"))
                browser.find_element_by_id('enterAddressCity').send_keys(unicode(add['city'], "utf-8"))
                browser.find_element_by_id('enterAddressStateOrRegion').send_keys(unicode(add['state'], "utf-8"))
                browser.find_element_by_id('enterAddressPostalCode').send_keys(add['zipcode'])
                browser.find_element_by_id('enterAddressPhoneNumber').send_keys(add['phoneno'])
                browser.find_element_by_id('enterAddressPhoneNumber').send_keys(Keys.RETURN)
            except:
                browser.find_element_by_id('address-ui-widgets-enterAddressFullName').send_keys(add['name'].encode("utf-8"))
                browser.find_element_by_id('address-ui-widgets-enterAddressLine1').send_keys(add['add1'].encode("utf-8"))
                browser.find_element_by_id('address-ui-widgets-enterAddressLine2').send_keys(add['add2'].encode("utf-8"))
                browser.find_element_by_id('address-ui-widgets-enterAddressCity').send_keys(unicode(add['city'], "utf-8"))
                browser.find_element_by_id('address-ui-widgets-enterAddressStateOrRegion').send_keys(unicode(add['state'], "utf-8"))
                browser.find_element_by_id('address-ui-widgets-enterAddressPostalCode').send_keys(add['zipcode'])
                browser.find_element_by_id('address-ui-widgets-enterAddressPhoneNumber').send_keys(add['phoneno'])
                browser.find_element_by_id('address-ui-widgets-enterAddressPhoneNumber').send_keys(Keys.RETURN)            
        else:
            pass
        time.sleep(5)
        try:
            if 'Suggested Address:' in browser.page_source:
                logMessageToCloud(loggroup,logstream, 'Suggested Address' ) 
                browser.find_element_by_xpath("//input[@type='submit' and @aria-labelledby='a-autoid-2-announce']").click()
        except:
            logMessageToCloud(loggroup,logstream, sys.exc_info()[0])
            logMessageToCloud(loggroup,logstream, 'Issue in address Submission' + unicode(add['name'], "utf-8"))

        try:
            browser.find_element_by_id('address-ui-widgets-enterAddressFullName')
            try:
                submitButton = browser.find_element_by_xpath("//input[@type='submit' and @class='a-button-input']").click()
            except:
                ##browser.find_element_by_id('address-ui-widgets-enterAddressPhoneNumber').send_keys(Keys.RETURN)
                logMessageToCloud(loggroup,logstream, sys.exc_info()[0])
                logMessageToCloud(loggroup,logstream, "Second Time Address Submit")
            
            time.sleep(5)
             
            try:
                browser.find_element_by_id('address-ui-widgets-enterAddressFullName')
                logMessageToCloud(loggroup,logstream, str(key) + 'Issue in address')
                deleteASINs.append(key)
            except:
                pass
        except:
            #print 'Outside'
            #print sys.exc_info()[0]
            pass
           
    time.sleep(5) 
    ## Add items to cart
    if cartissueflag == 0:
        AddOfferIDtoCart(browser,address,Offers)
        AddItemQuantity(browser,address,ordersno,mainqty)
    else:
        urldata = getTopUrl.split("&&")[0]
        #try:
        browser.get(link+"&"+urldata)
        
        time.sleep(4)
        try:
            browser.find_element_by_name('add').click()
        except:
            time.sleep(4)
            browser.find_element_by_name('add').click()
    
    try:    
        #wait.until(lambda browser: browser.find_element_by_id('sc-buy-box-gift-checkbox')) 
        browser.find_element_by_id('sc-buy-box-gift-checkbox').click()
        time.sleep(2)
        orderButton = browser.find_element_by_name("proceedToCheckout")
    except:
        time.sleep(2)
        orderButton = browser.find_element_by_name("proceedToCheckout")
    
    orderButton.click()
    
    time.sleep(5)
    browser.find_element_by_id("custom-fields-value-0").send_keys(Keys.TAB)    #chnge 
    
    submitButton=browser.find_element_by_id("a-autoid-0")                      #chnge 
    submitButton.click()                                                       #chnge 
    
    #submitButton = browser.switch_to.active_element
    #submitButton.send_keys(Keys.ENTER)
    
    time.sleep(3)    
    try:
        #wait.until(lambda browser: browser.find_element_by_xpath("//*[@data-pipeline-link-to-page='spp-ship-to-multiple']").click())
        browser.find_element_by_link_text("Ship to multiple addresses").click() 
    except:
        logMessageToCloud(loggroup,logstream, 'Not Able to click multiple address link')
        #browser.find_element_by_link_text("").click()
    time.sleep(3)
    for key in deleteASINs:
        try:
            browser.find_element_by_xpath("//*[@testid='delete-item-" + key + "']").click()
            addresssql="update b_order_details bd,b_orders b set mark = 1, trackingid = 1, our_order_status = 'Failed', our_order_status = 'Address issue' where itemasin = '" + key + "' and bd.amzOrderId=b.amzOrderId and bd.amzOrderId = '" + ordersno[key] + "' and (b.mark is null or trackingid is null)"
            logMessageToCloud(loggroup,logstream, addresssql)
            cursor.execute(addresssql)
            del address[key]
            del mainqty[key]
            del ordersno[key]
        except:
            logMessageToCloud(loggroup,logstream, 'Issue in Deleting Item '+  key)
            #sys.exit(0)
            ManualCheck(browser)
    
    if len(address) > 1:
        addrlen = len(address)
        curqty = 0
        for qtyval in mainqty.values():
            curqty += int(qtyval)
        logMessageToCloud(loggroup,logstream, "CurQty -" + str(curqty))
        if addrlen != curqty:
            addrlen = curqty
        for i in range(1,addrlen + 1):
            asinname = 'asin.' + str(i)
            addressname = 'addressID.destinationType.destinationId.destinationOwnerId.' + str(i)
            deleteasin = 'delete.' + str(i)
            currentASIN =str( browser.find_element_by_name(asinname).get_attribute("value"))
            logMessageToCloud(loggroup,logstream, currentASIN)
            logMessageToCloud(loggroup,logstream, str(address[currentASIN]))
            time.sleep(3)
            el = browser.find_element_by_name(addressname)
            tag = 0
            for option in el.find_elements_by_tag_name('option'):
                if 'Gold Deals LLC' in option.text:
                    option.click()            
                if address[currentASIN]['name'] in option.text:
                    option.click()
                    tag = 1
                    break
    else:
        try:
            nametomatch = address.itervalues().next()
            logMessageToCloud(loggroup,logstream, str(nametomatch['name']))
            time.sleep(3)
            selectaddrlst = browser.find_elements_by_css_selector(".displayAddressLI.displayAddressFullName")
            time.sleep(2)
            i = 0
            for curaddr in selectaddrlst:
                addrname = browser.find_element_by_id("address-book-entry-" + str(i)).find_element_by_link_text('Ship to this address')
                logMessageToCloud(loggroup,logstream, curaddr.text)
                if curaddr.text == str(nametomatch['name']):
                    logMessageToCloud(loggroup,logstream, 'Ready to CLick')
                    addrname.click()
                    break
                i = i+1
        except NoSuchElementException:
            logMessageToCloud(loggroup,logstream, "Error: Failed to choose Shipping Address")
            #browser.quit()
            #sys.exit()
            #ManualCheck(browser)

    logMessageToCloud(loggroup,logstream,str( deleteASINs))
    try:
        continueButton = browser.find_element_by_name("continue-bottom")
        continueButton.click()
    except:
        try:
            browser.find_element_by_name("continueMultiAddress").click()
        except:
            browser.find_element_by_xpath("//*[@type='submit']").click()
	
	DeleteIssueItemCheck(browser,address,ordersno,mainqty,"Address issue")
	
    try:
        time.sleep(10)
        if len(address) == 1:
            addrlen = 1
        else:
            curqty = 0
            for qtyval in mainqty.values():
                curqty += int(qtyval)
            logMessageToCloud(loggroup,logstream, "CurQty -" +  str(curqty))
            if addrlen != curqty:
                addrlen = curqty
        for i in range(0,addrlen):
            messageid = 'message-area-' + str(i)
            browser.find_element_by_id(messageid).clear()
            browser.find_element_by_id(messageid).send_keys('Thank You')
            browser.find_element_by_id("message-area-0").send_keys(Keys.TAB)      #chnge 
        submitButton=browser.find_element_by_id("mfnHidePriceCheckbox-1")         #chnge 
        submitButton.click()                                                      #chnge 
        #browser.find_element_by_id(messageid).send_keys(Keys.TAB)
        #submitButton = browser.switch_to.active_element
        #submitButton.click()
    except:
        time.sleep(3)
        submitButton=browser.find_element_by_xpath(".//*[@id='giftForm']/div[3]/div/div/span[1]/span/input")     #chnge
        submitButton.click()                                                                                     #chnge
        
        #submitButton = browser.switch_to.active_element
        #submitButton.send_keys(Keys.ENTER)
    time.sleep(3)
    try:
        browser.find_element_by_xpath("//*[@type='submit']").click()
    except:
        logMessageToCloud(loggroup,logstream, 'Submit 1')
        #browser.find_element_by_xpath("//*[@type='submit']").click()
    time.sleep(5)
    logMessageToCloud(loggroup,logstream, "Step 1")
    try:
        browser.find_element_by_xpath("//*[@type='submit']").click()
    except:
        logMessageToCloud(loggroup,logstream, 'Submit 2')
        time.sleep(2)
    logMessageToCloud(loggroup,logstream, "Step2" )
    
    try:
        giftbal = GetGiftCardBalance(browser)
        logMessageToCloud(loggroup,logstream, "Gift card available balance is -" +  str(giftbal))
        sqlquery = "insert ignore into giftcardbalance values (null, now(),'" + giftbal +"','" + str(sellerid) + "')"
        ##print sqlquery
        cursor.execute(sqlquery)
    except:
        pass
    time.sleep(4)
    try:
        browser.find_element_by_xpath("//*[@type='submit']").click()
    except:
        time.sleep(2)
        try:
            browser.find_element_by_id('continue-top').click()
        except:
            pass        
    time.sleep(4)
    
    try:
        browser.find_element_by_id('continue-top').click()
    except:
        pass
	
	DeleteIssueItemCheck(browser,address,ordersno,mainqty,"Limited Qty")
    time.sleep(2)
	
    try:
        itemlst = browser.find_elements_by_xpath(".//*[@id='spc-orders']/div")
    except:
        logMessageToCloud(loggroup,logstream, "Failed to get item list.Please check for element ID")
        browser.quit()
        sys.exit(0)

    logMessageToCloud(loggroup,logstream, "Item length -"  + str(len(itemlst)))
    itemlen = len(itemlst)
    if itemlen > 1:
        MatchAddress(browser,itemlen,address,ordersno,mainqty)
    
    ## Check Gift Message Exists or not
    try:
        itemlst1 = browser.find_elements_by_xpath(".//*[@id='spc-orders']/div")
    except:
        logMessageToCloud(loggroup,logstream, "Failed to get item list1.Please check for element ID")
        browser.quit()
        sys.exit(0)
        
    
    logMessageToCloud(loggroup,logstream, "Item1 length -" + str(len(itemlst1)))
    itemlen1 = len(itemlst1)
    
    CheckGiftMessage(browser,itemlen1)

    time.sleep(3)
    sys.exit(1)
    '''
    try:
        placeOrder = browser.find_element_by_name("placeYourOrder1")
        placeOrder.click()
        for key, val in ordersno.iteritems():
            if key in orderanywaylst:
                sqlupdate = "update b_order_details bd,b_orders b set mark = 1,trackingid = 1, our_order_status = 'Success' where itemasin = '" + key + "' and bd.amzOrderId=b.amzOrderId and bd.amzOrderId = '" + val + "' and (mark = 2 or trackingid = 1)"
                logMessageToCloud(loggroup,logstream, sqlupdate)
                cursor.execute(sqlupdate)
                sql2 = "delete from b_order_details_anyway where amzOrderId = '" + val + "'"
                cursor.execute(sql2)
                sql3 = "insert ignore into event_log values (null,'" + val + "','OrderedAnyWay',now(),null)"
                cursor.execute(sql3)
            else:
                sqlupdate = "update b_order_details bd,b_orders b set mark = 1,trackingid = 1, our_order_status = 'Success' where itemasin = '" + key + "' and bd.amzOrderId=b.amzOrderId and bd.amzOrderId = '" + val + "' and (mark is null or trackingid is null)"
                logMessageToCloud(loggroup,logstream, sqlupdate)
                cursor.execute(sqlupdate)
                sql3 = "insert ignore into event_log values (null,'" + val + "','Ordered',now(),null)"
                cursor.execute(sql3)
        db.commit()
    except:
        logMessageToCloud(loggroup,logstream, 'Issue in Placing Orders')
    '''
    try:
        pass
        #GetOrderCSV(db,cursor,browser)
    except:
        pass
    
    browser.quit()
    #sys.exit(0)
    
    
    #time.sleep(90)
    #browser.quit()
    #getCsv() 
    #return

## Function to get Gift Card Balance in Amazon Account
def CheckGiftBalance_AMZAccount(sellerid):
    print "entered CheckGiftBalance_AMZAccount " + str(sellerid)  #testing
    proxysql = "SELECT username,password,ip,port FROM `proxy` where id in (select proxy_id from amazon_account where id = '28')"
    print proxysql
    cursor.execute(proxysql)
    proxydetails = cursor.fetchone()
    if len(proxydetails) > 1:
        usrname = proxydetails[0]
        passwd = proxydetails[1].decode('base64')
        tokendata = '%s:%s' %(str(usrname),str(passwd))
        authtoken = b64encode(tokendata)
        #print authtoken
        ipaddr = proxydetails[2]
        portnum = proxydetails[3]
        profile = webdriver.FirefoxProfile()
        profile.set_preference("signon.autologin.proxy",True)
        profile.add_extension(extension="close_proxy.xpi")
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", str(ipaddr)) #james87778:P95JIEXd
        profile.set_preference("network.proxy.http_port", int(portnum))
        profile.set_preference("network.proxy.ssl", str(ipaddr)) #james87778:P95JIEXd
        profile.set_preference("network.proxy.ssl_port", int(portnum))
        profile.set_preference("extensions.closeproxyauth.authtoken",authtoken)
        profile.update_preferences()
        browser = webdriver.Firefox(firefox_profile=profile)
        
        browser.get("http://www.amazon.com/")
        time.sleep(4)
        if "Amazon" not in browser.title:
            logMessageToCloud(loggroup,logstream, "Proxy settings issue")
            subject = "Failed to open Firefox browser with Proxy Settings"
            message = "Please check for Proxy Username, Password, Port and IPAddress."
            Status = SendMail(subject, message)
            if Status:
                print "Email Sent Successfully"
                browser.quit()
                browser = webdriver.Firefox()
            else:
                print "Failed to send email.Please check for Email settings"
                #browser.quit()
                #sys.exit(0)
        #browser = webdriver.Firefox()
    else:
        browser = webdriver.Firefox() #firefox_profile=profile
    
    browser.implicitly_wait(10)
    
    try:
        browser.get("https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin")
    except TimeoutException:
        logMessageToCloud(loggroup,logstream, "Unable to load Amazon.com webpage. Script will reload page now.")
        browser.refresh()
    time.sleep(5)
    loginaccount(browser,1,sellerid)
    time.sleep(25)
    browser.get("https://www.amazon.com/gp/css/gc/balance?ref_=ya_d_c_gc")
    time.sleep(5)
    if "Gift Card Balance" not in browser.title:
        subject = "Failed to open Gift Card Balance Page"
        message = "Please check for whether we are able to Login to Amazon. Problem may also be due to Captcha issue while logging to Amazon."
        Status = SendMail(subject, message)
        if Status:
            print "Email Sent Successfully"
            #browser.quit()
            #sys.exit(0)
        else:
            print "Failed to send email.Please check for Email settings"
            #browser.quit()
            #sys.exit(0)
        ManualCheck(browser)
    
    giftdata = browser.find_element_by_class_name("gcBalance").text
    #print "Giftdata ---->",giftdata
    reobj = re.search("Your Gift Card Balance: \$([0-9\.\,]+)",giftdata)
    browser.quit()
    if reobj:
        bal_amount = reobj.group(1).strip()
        #print "Bal vall -",bal_amount
        availbal = bal_amount.split(",")
        balamount = float(''.join(availbal))
        return balamount
    else:
        logMessageToCloud(loggroup,logstream, "Failed to get Giftcard balance from Amazon Account")
        sys.exit(0)

## Delete Issue Item
def DeleteIssueItemCheck(browser,address,ordersno,mainqty,msgval):
    
    try:
        errblockmsg = browser.find_element_by_xpath(".//*[@class='errorblock message error']/div").text
        #print errblockmsg
    except:
        return
    spltdata = errblockmsg.split("\n")
    flag = 0
    itemlst = []
    for curline in spltdata:
        reobj1 = re.search("There was a problem with some of the items in your order",curline,re.I)
        if reobj1:
            flag = 1
            continue
        if flag == 1 and curline != '':
            itemlst.append(str(curline.strip()))
    
    logMessageToCloud(loggroup,logstream, "ErrorItemList" +  str(itemlst))
    for curitemval in itemlst:
        try:
            itemrowlist = browser.find_elements_by_class_name("itemrow ")
            #print itemrowlist
            #print len(itemrowlist)
        except:
            itemrowlist = []
        i = 1
        for curitemname in itemrowlist:
            #print str(curitemname.text)
            dataval1 = str(curitemname.text)
            spltval = dataval1.split("\n")
            itemname = spltval[0]
            itemname = str(itemname.strip())
            
            if itemname == str(curitemval):
                asinname = 'asin.' + str(i)
                currentASIN =str(browser.find_element_by_name(asinname).get_attribute("value"))
                logMessageToCloud(loggroup,logstream, currentASIN)
                
                deladdr = 'delete.' + str(i)
                browser.find_element_by_name(deladdr).click()
                logMessageToCloud(loggroup,logstream, "Successfully deleted Asin item from list : " + currentASIN)
                
                if address.has_key(currentASIN):
                    ## Updating issue item to server
                    primesql="update b_order_details bd,b_orders b set mark = 1, trackingid = 1, our_order_status = 'Failed', our_order_msg = '" + str(msgval) +"' where itemasin = '" + currentASIN + "' and bd.amzOrderId=b.amzOrderId and bd.amzOrderId = '" + ordersno[currentASIN] + "' and (b.mark is null or trackingid is null)"
                    sql2 = "insert ignore into event_log values (null,'" + ordersno[currentASIN] + "','Failed',now(),'" + str(msgval) + "')"
                    logMessageToCloud(loggroup,logstream, primesql)
                    cursor.execute(primesql)
                    cursor.execute(sql2)
                    
                    del address[currentASIN]
                    del ordersno[currentASIN]
                    del mainqty[currentASIN]
                ## Sending Alert mail
                subject = "Deleted Asin value %s from the order list" %(currentASIN)
                message = "We have successfully deleted Asin value %s from the order list due to %s." %(currentASIN,str(msgval))
                logMessageToCloud(loggroup,logstream, message)
                Status = SendMail(subject, message)
                if Status:
                    print "Email Sent Successfully"
                else:
                    print "Failed to send email.Please check for Email settings"
                    #browser.quit()
                    #sys.exit(0)
                
                itemrowlist.pop(i-1)
                time.sleep(3)
                break
            
            i += 1
    
    try:
        browser.find_element_by_name("continueMultiAddress").click()
    except:
        browser.find_element_by_xpath("//*[@type='submit']").click()


## Function to check Cart Quantity and delete the Asin if not matches
def CheckCartQuantity(cart,mainqty,mainordersno,mainaddress):
    cartid = cart.cart_id
    carthmac = cart.hmac
    getcart =  amazon.cart_get(CartId=cartid,HMAC=carthmac)
    itemid = {}
    errasin = []
    for i in getcart:
        itemasin = i.asin
        itemqty = i.quantity
        if int(mainqty[itemasin]) != int(itemqty):
            errasin.append(itemasin)
            cartitemid = i.cart_item_id
            itemid[itemasin] = cartitemid
    
    modifycartArray = []
    for curasin in itemid.keys():
        mainqty[curasin] = '0'
        modifycartArray.append({'cart_item_id':itemid[curasin],'quantity':mainqty[curasin]})               
        if curasin in errasin:
            primesql="update b_order_details bd,b_orders b set mark = 1, trackingid = 1, our_order_status = 'Failed', our_order_msg = 'Limited Qty' where itemasin = '" + curasin + "' and bd.amzOrderId=b.amzOrderId and bd.amzOrderId = '" + mainordersno[curasin] + "' and (b.mark is null or trackingid is null)"
            sql2 = "insert ignore into event_log values (null,'" + mainordersno[curasin] + "','Failed',now(),'Limited Qty')"
            logMessageToCloud(loggroup,logstream, primesql)
            cursor.execute(primesql)
            cursor.execute(sql2)
            
            del mainqty[curasin]
            del mainordersno[curasin]
            del mainaddress[curasin]
        
        time.sleep(2)
    
    if len(errasin) > 0:
        cart = amazon.cart_modify(modifycartArray,CartId=cartid,HMAC=carthmac)
        adduri = cart.purchase_url + '&SessionId=179-4136716-0818845&confirmPage=confirm&add.x=56&add.y=0&add=add'
        logMessageToCloud(loggroup,logstream,'Prime Add Uri '  + adduri)
        logMessageToCloud(loggroup,logstream,'Prime ' + str(cart.amount))
    
    return cart


## Manual Check
def ManualCheck(browser):
	time.sleep(100)
	return
	value1 = raw_input("Press \'yes\' to sys.exit() or \'no\' to do manual process by user: \n")
	value1 = str(value1).lower()
	if value1 == "yes":
		print "You have chosen sys.exit() option and program is exiting now.."
		browser.quit()
		sys.exit(0)
	else:
		raw_input("Please do the manual process and press any key to continue to next step\n")
		print "Continuing to next step...\n"


def AddOfferIDtoCart(browser,address,Offers):
    
    for key in address.keys():
        browser.get("https://www.amazon.com/gp/offer-listing/%s/ref=olp_f_new?ie=UTF8&f_new=true" %(key))
        time.sleep(2)
        getindex = Offers[key][3]
        try:
            browser.find_element_by_xpath(".//*[@id='olpOfferList']/div/div/div[%s]/div[5]/div/form/span" %(str(getindex))).click()
            time.sleep(2)
        except Exception as err:
            logMessageToCloud(loggroup,logstream, "Failed to Add item %s to cart"   + str(key))
            logMessageToCloud(loggroup,logstream, "Error -" + str(err))
            ## Sending Alert mail
            subject = "Failed to add Asin value %s to Cart" %(str(key))
            message = "Failed to add Asin value %s to Cart. Need to check manually" %(str(key))
            #print message
            Status = SendMail(subject, message)
            if Status:
                print "Email Sent Successfully"
            else:
                print "Failed to send email.Please check for Email settings"
            
            #browser.quit()
            #sys.exit(0)
            ManualCheck(browser)
        
        logMessageToCloud(loggroup,logstream, "Successfully added Asin value to cart"  + str(key))


def AddItemQuantity(browser,address,ordersno,mainqty):
    
    try:
        browser.get('https://www.amazon.com/gp/cart/view.html/ref=nav_bnav_cart')
        time.sleep(3)
    except NoSuchElementException:
        logMessageToCloud(loggroup,logstream, "Failed to enter Cart Menu")
        sys.exit(0)
    
    cartlen = GetCartLength(browser)
    for itemflag in range(1,len(mainqty) + 1):
        
        if cartlen == 1:
            getasinval = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div").get_attribute("data-asin")
            logMessageToCloud(loggroup,logstream, "Current Asin -" + getasinval)
            if mainqty.has_key(str(getasinval)):
                itemqty = mainqty[str(getasinval)]
                if int(itemqty) > 1:
                    qtyval = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div/div[4]/div/div[3]/div/div/span/select/option[%s]" %(str(itemqty)))
                    qtyval.click()
                    time.sleep(3)
                    alerttext = ''
                    try:
                        alerttext = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div/div[4]/div[1]/div/div/div/span").text
                        alerttext = alerttext.strip()
                    except:
                        pass
                    reobj = re.search("This seller has only (.*)",alerttext,re.I)
                    if reobj:
                        try:
                            delcart = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div/div[4]/div/div[1]/div/div/div[2]/div/span[1]/span/input")
                            delcart.click()
                            logMessageToCloud(loggroup,logstream, "Sucessfully deleted Cart Item  may be due to Out of Stock "  + str(getasinval))
                            ## Sending Alert mail
                            subject = "Sucessfully deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            message = "We have sucessfully deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            #print message
                            Status = SendMail(subject, message)
                            if Status:
                                print "Email Sent Successfully"
                            else:
                                print "Failed to send email.Please check for Email settings"
                                #browser.quit()
                                #sys.exit(0)
                                
                            del address[str(getasinval)]
                            del ordersno[str(getasinval)]
                            del mainqty[str(getasinval)]
                        except Exception as err:
                            print "Err -",err
                            print "Failed to deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            ## Sending Alert mail
                            subject = "Failed to deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            message = "Failed to deleted Cart Item %s may be due to Out of Stock. Need to check Manually." %(str(getasinval))
                            #print message
                            Status = SendMail(subject, message)
                            if Status:
                                print "Email Sent Successfully"
                            else:
                                print "Failed to send email.Please check for Email settings"
                            #browser.quit()
                            #sys.exit(0)
                            ManualCheck(browser)
 
                    logMessageToCloud(loggroup,logstream, "Sucessfully added Asin value %s to quantity %s" %(str(getasinval),str(itemqty)))
        
        else:
            getasinval = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div[%s]" %(str(itemflag))).get_attribute("data-asin")
            logMessageToCloud(loggroup,logstream, "Current Asin -" + getasinval)
            if mainqty.has_key(str(getasinval)):
                itemqty = mainqty[str(getasinval)]
                if int(itemqty) > 1:
                    qtyval = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div[%s]/div[4]/div/div[3]/div/div/span/select/option[%s]" %(str(itemflag),str(itemqty)))
                    qtyval.click()
                    time.sleep(3)
                    alerttext = ''
                    try:
                        alerttext = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div[%s]/div[4]/div[1]/div/div/div/span" %(str(itemflag))).text
                        alerttext = alerttext.strip()
                    except:
                        pass
                    reobj = re.search("This seller has only (.*)",alerttext,re.I)
                    if reobj:
                        try:
                            delcart = browser.find_element_by_xpath(".//*[@id='activeCartViewForm']/div[2]/div[%s]/div[4]/div/div[1]/div/div/div[2]/div/span[1]/span/input" %(str(itemflag)))
                            delcart.click()
                            logMessageToCloud(loggroup,logstream, "Sucessfully deleted Cart Item %s may be due to Out of Stock" %(str(getasinval)))
                            ## Sending Alert mail
                            subject = "Sucessfully deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            message = "We have sucessfully deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            #print message
                            Status = SendMail(subject, message)
                            if Status:
                                print "Email Sent Successfully"
                            else:
                                print "Failed to send email.Please check for Email settings"
                                #browser.quit()
                                #sys.exit(0)
                            
                            del address[str(getasinval)]
                            del ordersno[str(getasinval)]
                            del mainqty[str(getasinval)]
                        
                        except Exception as err1:
                            logMessageToCloud(loggroup,logstream, "Err1 -" +  str(err1))
                            print "Failed to deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            ## Sending Alert mail
                            subject = "Failed to deleted Cart Item %s may be due to Out of Stock" %(str(getasinval))
                            message = "Failed to deleted Cart Item %s may be due to Out of Stock. Need to check Manually." %(str(getasinval))
                            
                            Status = SendMail(subject, message)
                            if Status:
                                print "Email Sent Successfully"
                            else:
                                print "Failed to send email.Please check for Email settings"
                            
                            #browser.quit()
                            #sys.exit(0)
                            ManualCheck(browser)                                        
                    print "Sucessfully added Asin value %s to quantity %s" %(str(getasinval),str(itemqty))
            


#try:

amazon = AmazonAPI('AKIAJKK3FONKVMZSUKIQ', 'podbDqWA/3lWJagHMFytp59QsWs2wTtTo4J22Ikg', 'topcacom-20')
print "execution satarted" #testing
db = MySQLdb.connect("52.10.254.95","autoebayorders","YqS57LF27qp2J4bD","auto_warehousedeals")
cursor = db.cursor()
logstream = 'Orders' + '-' + str(datetime.datetime.now().date())
dbsql = "SHOW DATABASES LIKE 'auto\_%' "
#dbsql = "SHOW DATABASES LIKE 'auto\_warehousedeals'"
cursor.execute(dbsql)
dblist = cursor.fetchall()
for dbTuple in dblist:
    print dbTuple[0]
    db.select_db(dbTuple[0])
    sellersql = "select distinct seller,amazon from ebay_token where seller is not null and amazon in ('25','26','27')"
    cursor.execute(sellersql)
    sellerlist = cursor.fetchall()
    for sellerrow in sellerlist:
        sellername = sellerrow[0]
        print sellername  #testing
        sellerid = sellerrow[1] 
        print sellerid #testing
        loggroup = sellername
        logMessageToCloud(loggroup,logstream, 'Process Started : ' + sellername + ' ,' + str(sellerid))
        #sys.exit()
        sqlC = "SELECT count(amzOrderId), sum(ordertotal)  FROM (select  amzOrderId , ordertotal from `b_orders` WHERE seller= '" + sellername + "' and mark is null and OrderStatus = 'Completed' and orderdate > '2017-03-06' limit 5) t1"
        print sqlC  #testing
        cursor.execute(sqlC)
        resp = cursor.fetchall()
        print resp # testing
        ## Get Giftcard balance from DB
        giftbalsql = "SELECT balance FROM `giftcardbalance` WHERE sellerid= '" + str(sellerid) + "' order by date desc limit 1"
        cursor.execute(giftbalsql)
        respval = cursor.fetchall()
        giftamount = float(str(respval[-1][0]).strip("$"))
        ## Adding 10%per value to giftcardbalance
        giftbalper = round((giftamount/100) * 20, 2)
        maingiftbal = giftamount + giftbalper
        logMessageToCloud(loggroup,logstream, "Giftcard balance Amount(with 20% delivery charges) -"  + str(maingiftbal))
        errflag = 0
        orderamount = 0
        for cnt in resp:
            if str(cnt[1]) == "None" or (int(cnt[1]) > 1 and int(cnt[1]) < 50):
                logMessageToCloud(loggroup,logstream, "Order Total less than $50 for Database " + str(dbTuple[0]))
                errflag = 1
            else:
                orderamount = float(cnt[1])
                logMessageToCloud(loggroup,logstream, "Order total Amount -" + str(orderamount))
        if errflag == 1:
            continue
        print "maingiftbal < orderamount" + str(maingiftbal) + " < " + str(orderamount)
        if maingiftbal < orderamount:
            print "calling CheckGiftBalance_AMZAccount with seller id" + str(sellerid)
            actualbal = CheckGiftBalance_AMZAccount(sellerid)
            logMessageToCloud(loggroup,logstream, "Actual GiftCard Balance from AMZ Account -" + str(actualbal))
            if actualbal < orderamount:
                subject = "Gift card balance is less than Order total Amount for Database %s" %(str(dbTuple[0]))
                message = "We found that Gift card balance is less than Order total Amount for Database %s.Please add giftcard balance to the account immediately" %(str(dbTuple[0]))
                Status = SendMail(subject, message)
                if Status:
                    print "Email Sent Successfully"
                    continue
                else:
                    print "Failed to send email.Please check for Email settings"
                    continue
        
        sql = "SELECT `orderdate`,b.amzOrderId , itemasin, itemprice, itemqty,`ship_name`,`ship_address_1`,`ship_address_2`, `ship_city`,`ship_state_region`,`ship_country`,`ship_zip`,`ship_phone` FROM  b_order_details bd , \
        b_orders b where bd.`amzOrderId` = b.amzOrderId and seller= '" + sellername + "' and (b.mark is null or (b.mark = 1 and bd.trackingid is null)) and OrderStatus = 'Completed' and prime = 1 and orderdate > '2017-03-06' order by orderdate asc limit 9"
        
        sqlanyway = "SELECT `orderdate`,b.amzOrderId , itemasin, itemprice, itemqty,`ship_name`,`ship_address_1`,`ship_address_2`, `ship_city`,`ship_state_region`,`ship_country`,`ship_zip`,`ship_phone` FROM  b_order_details bd , \
        b_orders b where bd.`amzOrderId` = b.amzOrderId and seller= '" + sellername + "' and (b.mark = 2 or (b.mark = 2 and bd.trackingid is null)) and OrderStatus = 'Completed' and prime = 1  and orderdate > '2017-03-06' order by orderdate desc limit 1"
        
        sqlcmd = [sql,sqlanyway]
        sflag = 0
        mainordersno = {}
        mainaddress = {}
        mainasins = []
        mainqty = {}
        Offers = {}
        orderanywaylst = []
        for curcmd in sqlcmd:
            sflag += 1
            cursor.execute(curcmd)

            results = cursor.fetchall()
            cnt = 0;
            asins=[]
            qty={}
            ordersno={}
            address={}
            price={}
            for row in results:
                asins.append(row[2])
                qty[row[2]]=row[4]
                ordersno[row[2]]=row[1]
                price[row[2]]=row[3]
                if row[12] is None or len(row[12]) < 3:
                    phone = '+1'
                else:
                    phone = row[12]
                if row[10] == 'US':
                    addline2 = row[7] if row[7] is not None else ''        
                    address[row[2]]={'name':' '.join(row[5].encode('ascii','ignore').split()),'add1':row[6].encode('ascii','ignore'),'add2':addline2.encode('ascii','ignore'),'city':row[8],'state':row[9],'zipcode':row[11],'country':row[10],'phoneno':phone}
                else:
                    #address[row[2]]={'name':' '.join(row[5].split()),'add1':row[6],'add2':row[7],'city':row[8],'state':row[9],'zipcode':row[11],'country':row[10],'phoneno':phone}
                    address[row[2]]={'name':'GID - HIPSHIPPER - ' + row[1] ,'add1':'984 E 35TH STREET','add2':row[1],'city':'BROOKLYN','state':'NY','zipcode':'11210','country':'US','phoneno':'1800123456789'}
                
            
            logMessageToCloud(loggroup,logstream, str(asins))
            logMessageToCloud(loggroup,logstream, str(price))
            logMessageToCloud(loggroup,logstream, str(ordersno))
            
            psql = "SELECT seller_type,min_profit_per+ebay_paypal_fee,min_profit FROM `priority_buying` where status=1 ORDER BY `priority_buying`.`order` ASC"
            cursor.execute(psql)
            presp = cursor.fetchall()
            print presp #testing
            
            proritydatalst = []
            minconstantdatalst = []
            for curdata in presp:
                proritydatalst.append((curdata[0],curdata[1]))
                minconstantdatalst.append((curdata[0],curdata[2]))
            proritydata = tuple(proritydatalst)
            logMessageToCloud(loggroup,logstream,str(proritydata))
            minconstantdata = tuple(minconstantdatalst)
            logMessageToCloud(loggroup,logstream,"Minimum Constant Data" + str(minconstantdata))
            
            psql2 = "SELECT review_per,review_count FROM `review_count`"
            cursor.execute(psql2)
            presp2 = cursor.fetchall()
            
            items = {}
            items["item"] = price
            items["priority"] = proritydata
            sellerRating = {}
            sellerRating['rating'] = presp2[0][0]
            sellerRating['reviews'] = presp2[0][1]
            items['min_profit_constant'] = minconstantdata
            items["sellerRating"] = sellerRating
            
            if sflag == 1:
                logMessageToCloud(loggroup,logstream, "Items -" + ",".join(items))
                Offersdict = CheckMarginBasedPriority(items,loggroup,logstream)
            else:
                items["orderanyway"] = 'true'
                logMessageToCloud(loggroup,logstream, "Items -" + ",".join(items))
                Offersdict = CheckMarginBasedPriority(items,loggroup,logstream)
                orderanywaylst = Offersdict.keys()
        
            print "Offersdict = ",Offersdict #testing
            Offers.update(Offersdict)
            mainordersno.update(ordersno)
            mainaddress.update(address)
            mainqty.update(qty)
            mainasins.extend(asins)
            
        logMessageToCloud(loggroup,logstream, "Offers =" + str(Offers))
        print str(Offers) #testing
        
        try:
            
            asin = ",".join(mainasins)
            cartArray = []
            displaymsglst = ["Out of Stock"]
            for curasin in Offers.keys():
                logMessageToCloud(loggroup,logstream, "Current Asin value -" + curasin)
                failflag = 0
                if type(Offers[curasin]) == tuple:
                    cartArray.append({'offer_id':Offers[curasin][1],'quantity':mainqty[curasin]})
                    sqlval3 = "update b_order_details bd,b_orders b set channel='"+str(Offers[curasin][0])+"' where itemasin = '" + curasin + "' and bd.amzOrderId=b.amzOrderId and bd.amzOrderId = '" + mainordersno[curasin] + "' and (b.mark is null or trackingid is null)"
                    cursor.execute(sqlval3)
                    db.commit()
                else:
                    failflag = 1
                if failflag == 1:
                    primesql="update b_order_details bd,b_orders b set mark = 1, trackingid = 1, our_order_status = 'Failed', our_order_msg = '" + Offers[curasin] +"' where itemasin = '" + curasin + "' and bd.amzOrderId=b.amzOrderId and bd.amzOrderId = '" + mainordersno[curasin] + "' and (b.mark is null or trackingid is null)"
                    sql2 = "insert ignore into event_log values (null,'" + mainordersno[curasin] + "','Failed',now(),'" + Offers[curasin] + "')"
                    logMessageToCloud(loggroup,logstream, primesql)
                    cursor.execute(primesql)
                    cursor.execute(sql2)
                    del mainordersno[curasin]
                    del mainaddress[curasin]
                    del mainqty[curasin]
                    db.commit()
                
            #print cartArray
            if len(cartArray) != 0:
                cartflag = 1
                cartissueflag = 0
                while cartflag <= 2:
                    try:
						cart =  amazon.cart_create(cartArray)
						adduri = cart.purchase_url + '&SessionId=179-4136716-0818845&confirmPage=confirm&add.x=56&add.y=0&add=add'
						logMessageToCloud(loggroup,logstream, adduri)
						logMessageToCloud(loggroup,logstream, str(cart.amount))
    
						## Checks Cart Quantity
						cart = CheckCartQuantity(cart,mainqty,mainordersno,mainaddress)
						
						cartissueflag = 1
                    except Exception as e:
                        logMessageToCloud(loggroup,logstream, "Exception -" +  str(e))
                        if cartflag == 2:
                            break
                    time.sleep(15)
                    cartflag += 1
                
                if cartissueflag == 0:
                    #print "Something Issue while adding cart items"
                    cartamount = 0
                    for curkey in mainaddress.keys():
                        cartamount += (float(Offers[curkey][2]) * int(mainqty[curkey]))
                    logMessageToCloud(loggroup,logstream, "Cart Amount -" +  str(cartamount))
                    
                    adduri = ''
                    if int(cartamount) > 50:
                        placeOrder(adduri,mainordersno,mainaddress,orderanywaylst,sellerid,mainqty,cartissueflag,Offers)  
                    else:
                        logMessageToCloud(loggroup,logstream, "Cart Amount less than $50")
                    
                else: 
                     
                    if (int(cart.amount)/100) > 50:
                        placeOrder(adduri,mainordersno,mainaddress,orderanywaylst,sellerid,mainqty,cartissueflag,Offers)  
                    else:
                        logMessageToCloud(loggroup,logstream, "Cart Amount less than $50")
                
        
        except MySQLdb.Error as e:
            print e
            logMessageToCloud(loggroup,logstream, "Unexpected error:" +  sys.exc_info()[0] + 'Out : ' + asin)
            pass    
  