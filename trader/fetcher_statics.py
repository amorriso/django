import pdb
import selenium.webdriver as webdriver
import bs4 as bs
import logging
import os
import time
import projectX.libs.utility_functions as utils

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

settings = utils.load_settings('settings.global')

class ScrapeStatics(object):


    def __init__(self):
        pass


    @staticmethod
    def get_first_block(bsobject, block, attrs = None, subset = False):

        '''
        Return <block> as specified by the attributes in attrs dict.

        THIS FUNCTION WILL ONLY RETURN A BLOCK THAT HAVE ATTRIBUTES THAT MATCH
        THOSE SPECIFIED IN attrs EXACTLY

        Inputs:
            block, string <div>, <a>, <p> etc ..
            attrs, dict, e.g. {'class' : 'nav-item-content', 'js-nav-item' }

        Outputs:
            first <block> that matches with associated attributes.
        '''

        l = ScrapeStatics.get_blocks(bsobject, block, attrs, subset)

        if l is None:
            return None

        if len(l) > 0:
            return l[0]
        else:
            return None


    @staticmethod
    def get_blocks(bsobject, block, attrs = None, subset = False):

        '''
        Return all <block>'s in a list as specified by the attributes in 
        attrs dict.

        THIS FUNCTION WILL ONLY RETURN BLOCKS THAT HAVE ATTRIBUTES THAT MATCH
        THOSE SPECIFIED IN attrs EXACTLY

        Inputs:
            block, string <div>, <a>, <p> etc ..
            attrs, dict, e.g. {'class' : ['nav-item-content', 'js-nav-item'] }

        Outputs:
            List containing <block>'s that matches with associated
            attributes.
        '''

        if attrs:
            for k, v in attrs.items():
                if type(v) != type([]):
                    message = "attr vals should be specified in a list '[]'!"
                    raise ValueError(message)
                # yes. We f'ing sort the attrs list because later on we go:
                # if ref_dict == attrs: -> this recognises the ordering!!?? fuck
                attrs[k] = sorted(v)

        l = bsobject.findAll(block, attrs)

        if l is None:
            return None

        if len(l) == 0:
            return None

        if attrs:
            refined = []
            for e in l:
                # the line below allows us to filter on just the attributes
                # we've specified. Ignoring other attributes we can't be 
                # bothered to specify or don't know before hand.
                #if dict([(k, e.attrs[k]) for k in attrs]) == attrs:
                #    refined.append(e)

                #ref_dict = dict([(k, sorted(e.attrs[k])) for k in attrs])
                ref_dict = {}
                for k in attrs:
                    if len(attrs[k]) == 1:
                        ref_dict[k] = e.attrs[k]
                    else:
                        ref_dict[k] = sorted(e.attrs[k])

                for k in ref_dict.keys():
                    if type(ref_dict[k]) != type([]):
                        ref_dict[k] = [ref_dict[k]]

                if not subset:
                    if ref_dict == attrs:
                        refined.append(e)
                else:
                    issubset = True
                    for k, v in attrs.items():
                        if not set(v).issubset(set(ref_dict[k])):
                            issubset = False
                            break
                    if issubset:
                        refined.append(e)

                #pdb.set_trace()

            return refined
        else:
            return l


    @staticmethod
    def get_url_as_bs_instantiatedriver(url, wait_sequence = [], test = None):
        '''
        
        '''

        if not test:
            try:
                driver = webdriver.PhantomJS(
                        executable_path = settings['phantomjs'],
                        service_log_path = settings['phantomjslog']
                    )
                driver.get(url)
                source = driver.page_source.encode('utf8')
            except TimeoutException:
                pass
            except:
                logging.warning('driver failed to get url: {0}'.format(url))
                
            finally:
                driver.quit()
                
            bs_object = ScrapeStatics.get_url_as_bs(
                    driver,
                    url,
                    wait_sequence = wait_sequence,
                    test = test
                )
            try:
                driver.quit()
            except:
                m = "driver couldn't quit for some reason, may not exist!??"
                logging.error(m)
            
            return bs_object
            #return bs.BeautifulSoup(source, 'html.parser')

        else:
            if type(test) == type(""):
                return bs.BeautifulSoup(open(test).read(), 'html.parser')
            else:
                message = "test arg must specify .html file name and path"
                raise ValueError(message)


    @staticmethod
    def refresh(driver, wait_sequence = [], test = None):

        '''
        refresh page(/iframe/frame on page)

        Inputs:
            wait_sequence -> [
                    ("identifier=tag", [list of 'frame' tags), 
                    (x, [Y, Z]), ...
                ]

        Outputs:
            None

        Example wait_sequence:
            [
                ("id=site_sports", ['site_sports', 'main'], 
                    ("id=runnerListViewContainer", [])
            ]
            This will wait until id="site_sports" is present on the page. Then
            switch to the 'site_sports' iframe then the 'main' frame (BetFair).
            Then, it will wait for id='runnerListViewContainer' to be present
            before returning.

        '''

        if test:
            return None

        # fix for imputable type default kwarg!!
        if wait_sequence is None:
            wait_sequence = []

        if len(wait_sequence) == 0:
            driver.refresh()
            return
        else:
            if type(wait_sequence) != type([]):
                m = "wait_sequence must be list!"
                raise TypeError(m)
            for e in wait_sequence:
                if type(e) != type(()):
                    m = "wait_sequence elements must be tuples!"
                    raise TypeError(m)
                if type(e[0]) != type(""):
                    m = "first element in wait_sequence tuple must be string"
                    raise TypeError(m)
                if len(e[0].split('=')) != 2:
                    m = "first element in wait_sequence tuple must be a "+\
                            "string that specifies tag=value e.g. "+\
                            "'id=site_sports' specifies the tag and value!"
                    raise ValueError(m)
                if type(e[1]) != type([]):
                    m = "second element in wait_sequence tuple must be list!"
                    raise TypeError(m)

            driver.refresh()
            for e in wait_sequence:
                split_e0 = e[0].split('=')
                if split_e0[0] == 'id':
                    try:
                        element = WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located(
                                        (By.ID, split_e0[1])
                                    )
                            )
                    except:
                        m = "Frame "+e[0]+" failed to load in 30 seconds."
                        raise RuntimeError(m)
                elif split_e0[0] == 'class':
                    try:
                        element = WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located(
                                        (By.CLASS_NAME, split_e0[1])
                                    )
                            )
                    except:
                        m = "Frame "+e[0]+" failed to load in 30 seconds."
                        raise RuntimeError(m)
                else:
                    m = "You've only mapped id and class at this point! "+\
                            "you need to write the code to map anything else"
                    raise NotImplementedError(m)

                for frame in e[1]:
                    try:
                        # FUCKING BUG IN SELENIUM!!!!! find_element_by_name
                        # doesn't work sometimes. WTF people!?, in this case
                        # try by id. Fail is both of these don't work
                        frame_element = driver.find_element_by_name(frame)
                    except:
                        frame_element = driver.find_element_by_id(frame)

                    #try:
                    driver.switch_to.frame(frame_element)
                    #except Exception as error:
                    #    pdb.set_trace()

            time.sleep(1)



    @staticmethod
    def navigate(driver, url, wait_sequence = [], test = None):

        '''
        Navigate to a page(/iframe/frame on page)

        Inputs:
            url, string -> url
            wait_sequence -> [
                    ("identifier=tag", [list of 'frame' tags), 
                    (x, [Y, Z]), ...
                ]

        Outputs:
            None

        Example wait_sequence:
            [
                ("id=site_sports", ['site_sports', 'main'], 
                    ("id=runnerListViewContainer", [])
            ]
            This will wait until id="site_sports" is present on the page. Then
            switch to the 'site_sports' iframe then the 'main' frame (BetFair).
            Then, it will wait for id='runnerListViewContainer' to be present
            before returning.

        '''

        if test:
            return None

        # fix for imputable type default kwarg!!
        if wait_sequence is None:
            wait_sequence = []

        if len(wait_sequence) == 0:
            try:
                driver.get(url)
            except TimeoutException:
                pass
            return
        else:
            if type(wait_sequence) != type([]):
                m = "wait_sequence must be list!"
                raise TypeError(m)
            for e in wait_sequence:
                if type(e) != type(()):
                    m = "wait_sequence elements must be tuples!"
                    raise TypeError(m)
                if type(e[0]) != type(""):
                    m = "first element in wait_sequence tuple must be string"
                    raise TypeError(m)
                if len(e[0].split('=')) != 2:
                    m = "first element in wait_sequence tuple must be a "+\
                            "string that specifies tag=value e.g. "+\
                            "'id=site_sports' specifies the tag and value!"
                    raise ValueError(m)
                if type(e[1]) != type([]):
                    m = "second element in wait_sequence tuple must be list!"
                    raise TypeError(m)

            try:
                driver.get(url)
            except TimeoutException:
                pass
            for e in wait_sequence:
                split_e0 = e[0].split('=')
                if split_e0[0] == 'id':
                    try:
                        element = WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located(
                                        (By.ID, split_e0[1])
                                    )
                            )
                    except:
                        m = "Frame "+e[0]+" failed to load in 30 seconds."
                        raise RuntimeError(m)
                elif split_e0[0] == 'class':
                    try:
                        element = WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located(
                                        (By.CLASS_NAME, split_e0[1])
                                    )
                            )
                    except:
                        m = "Frame "+e[0]+" failed to load in 30 seconds."
                        raise RuntimeError(m)
                else:
                    m = "You've only mapped id and class at this point! "+\
                            "you need to write the code to map anything else"
                    raise NotImplementedError(m)

                for frame in e[1]:
                    try:
                        # FUCKING BUG IN SELENIUM!!!!! find_element_by_name
                        # doesn't work sometimes. WTF people!?, in this case
                        # try by id. Fail is both of these don't work
                        frame_element = driver.find_element_by_name(frame)
                    except:
                        frame_element = driver.find_element_by_id(frame)

                    #try:
                    driver.switch_to.frame(frame_element)
                    #except Exception as error:
                    #    pdb.set_trace()


    @staticmethod
    def get_url_as_bs(driver, url, wait_sequence = [], dosleep = True, 
            test = None, fail_str = None
        ):

        '''
        for description of wait_sequence see navigate.
        '''

        logging.debug('')

        if not test:
            ScrapeStatics.navigate(driver, url, wait_sequence = wait_sequence)
            oldsource = None
            counter = 0
            while True:
                source = driver.page_source.encode('utf8')
                if not fail_str is None:
                    if fail_str in source:
                        m = "Found fail_str in page source: " +\
                                url
                        raise RuntimeError(m)
                if oldsource == source:
                    break
                if counter > 150:
                    m = "page is taking too long to load. Fuck this shit: " +\
                            url
                    raise RuntimeError(m)
                counter += 1
                oldsource = source
                if dosleep:
                    time.sleep(0.1)
                
            return bs.BeautifulSoup(source, 'html.parser')
        else:
            if type(test) == type(""):
                return bs.BeautifulSoup(open(test).read(), 'html.parser')
            else:
                message = "test arg must specify .html file name and path"
                raise ValueError(message)


    @staticmethod
    def get_url_as_string(driver, url, wait_sequence = [], dosleep = True, 
            test = None, fail_str = None
        ):

        '''
        for description of wait_sequence see navigate.
        '''

        logging.debug('')

        if not test:
            ScrapeStatics.navigate(url, wait_sequence = wait_sequence)
            oldsource = None
            counter = 0
            while True:
                source = driver.page_source.encode('utf8')
                if not fail_str is None:
                    if fail_str in source:
                        m = "Found fail_str in page source: " +\
                                url
                        raise RuntimeError(m)
                if oldsource == source:
                    break
                if counter > 150:
                    m = "page is taking too long to load. Fuck this shit, "+\
                            "raising exception!"
                    raise RuntimeError(m)
                counter += 1
                oldsource = source
                if dosleep:
                    time.sleep(0.1)

            return source.encode("utf8")
        else:
            if type(test) == type(""):
                return open(test).read()
            else:
                message = "test arg must specify .html file name and path"
                raise ValueError(message)





