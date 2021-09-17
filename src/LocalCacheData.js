class LocalCacheData {

    constructor() {

    }

    fetcha(uri, options, ttl) {
        if (this.storageAvailable('localStorage')) {
            var lastLoading = localStorage.getItem(uri) ;            
            if ((Date.now() - lastLoading) > ttl) {
                localStorage.setItem(uri, Date.now()) ;
                options.cache = 'reload' ;
                return fetch(uri, options) ;
            } else {
                options.cache = 'force-cache' ;
                return fetch(uri, options) ;
            }
        } else {
            return fetch(uri, options) ;
        }
    }


    storageAvailable(type) {
        try {
            var storage = window[type],
                x = '__storage_test__';
            storage.setItem(x, x);
            storage.removeItem(x);
            return true;
        }
        catch(e) {
            return e instanceof DOMException && (
                // everything except Firefox
                e.code === 22 ||
                // Firefox
                e.code === 1014 ||
                // test name field too, because code might not be present
                // everything except Firefox
                e.name === 'QuotaExceededError' ||
                // Firefox
                e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
                // acknowledge QuotaExceededError only if there's something already stored
                storage.length !== 0;
        }
    }
}

module.exports = {
	LocalCacheData: LocalCacheData
}