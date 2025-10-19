/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./assets/src/js/api.js":
/*!******************************!*\
  !*** ./assets/src/js/api.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/**
 * List API on backend
 *
 * @since 4.2.6
 * @version 1.0.0
 */

const lplistAPI = {};
if ('undefined' !== typeof lpDataAdmin) {
  lplistAPI.admin = {
    apiAdminNotice: lpDataAdmin.lp_rest_url + 'lp/v1/admin/tools/admin-notices',
    apiAdminOrderStatic: lpDataAdmin.lp_rest_url + 'lp/v1/orders/statistic',
    apiAddons: lpDataAdmin.lp_rest_url + 'lp/v1/addon/all',
    apiAddonAction: lpDataAdmin.lp_rest_url + 'lp/v1/addon/action-n',
    apiAddonsPurchase: lpDataAdmin.lp_rest_url + 'lp/v1/addon/info-addons-purchase',
    apiSearchCourses: lpDataAdmin.lp_rest_url + 'lp/v1/admin/tools/search-course',
    apiSearchUsers: lpDataAdmin.lp_rest_url + 'lp/v1/admin/tools/search-user',
    apiAssignUserCourse: lpDataAdmin.lp_rest_url + 'lp/v1/admin/tools/assign-user-course',
    apiUnAssignUserCourse: lpDataAdmin.lp_rest_url + 'lp/v1/admin/tools/unassign-user-course',
    apiAJAX: lpDataAdmin.lp_rest_url + 'lp/v1/load_content_via_ajax/'
  };
}
if ('undefined' !== typeof lpData) {
  lplistAPI.frontend = {
    apiWidgets: lpData.lp_rest_url + 'lp/v1/widgets/api',
    apiCourses: lpData.lp_rest_url + 'lp/v1/courses/archive-course',
    apiAJAX: lpData.lp_rest_url + 'lp/v1/load_content_via_ajax/',
    apiProfileCoverImage: lpData.lp_rest_url + 'lp/v1/profile/cover-image'
  };
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (lplistAPI);

/***/ }),

/***/ "./assets/src/js/utils.js":
/*!********************************!*\
  !*** ./assets/src/js/utils.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   listenElementCreated: () => (/* binding */ listenElementCreated),
/* harmony export */   listenElementViewed: () => (/* binding */ listenElementViewed),
/* harmony export */   lpAddQueryArgs: () => (/* binding */ lpAddQueryArgs),
/* harmony export */   lpAjaxParseJsonOld: () => (/* binding */ lpAjaxParseJsonOld),
/* harmony export */   lpClassName: () => (/* binding */ lpClassName),
/* harmony export */   lpFetchAPI: () => (/* binding */ lpFetchAPI),
/* harmony export */   lpGetCurrentURLNoParam: () => (/* binding */ lpGetCurrentURLNoParam),
/* harmony export */   lpOnElementReady: () => (/* binding */ lpOnElementReady),
/* harmony export */   lpSetLoadingEl: () => (/* binding */ lpSetLoadingEl),
/* harmony export */   lpShowHideEl: () => (/* binding */ lpShowHideEl)
/* harmony export */ });
/**
 * Utils functions
 *
 * @param url
 * @param data
 * @param functions
 * @since 4.2.5.1
 * @version 1.0.3
 */
const lpClassName = {
  hidden: 'lp-hidden',
  loading: 'loading'
};
const lpFetchAPI = (url, data = {}, functions = {}) => {
  if ('function' === typeof functions.before) {
    functions.before();
  }
  fetch(url, {
    method: 'GET',
    ...data
  }).then(response => response.json()).then(response => {
    if ('function' === typeof functions.success) {
      functions.success(response);
    }
  }).catch(err => {
    if ('function' === typeof functions.error) {
      functions.error(err);
    }
  }).finally(() => {
    if ('function' === typeof functions.completed) {
      functions.completed();
    }
  });
};

/**
 * Get current URL without params.
 *
 * @since 4.2.5.1
 */
const lpGetCurrentURLNoParam = () => {
  let currentUrl = window.location.href;
  const hasParams = currentUrl.includes('?');
  if (hasParams) {
    currentUrl = currentUrl.split('?')[0];
  }
  return currentUrl;
};
const lpAddQueryArgs = (endpoint, args) => {
  const url = new URL(endpoint);
  Object.keys(args).forEach(arg => {
    url.searchParams.set(arg, args[arg]);
  });
  return url;
};

/**
 * Listen element viewed.
 *
 * @param el
 * @param callback
 * @since 4.2.5.8
 */
const listenElementViewed = (el, callback) => {
  const observerSeeItem = new IntersectionObserver(function (entries) {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        callback(entry);
      }
    }
  });
  observerSeeItem.observe(el);
};

/**
 * Listen element created.
 *
 * @param callback
 * @since 4.2.5.8
 */
const listenElementCreated = callback => {
  const observerCreateItem = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.addedNodes) {
        mutation.addedNodes.forEach(function (node) {
          if (node.nodeType === 1) {
            callback(node);
          }
        });
      }
    });
  });
  observerCreateItem.observe(document, {
    childList: true,
    subtree: true
  });
  // End.
};

/**
 * Listen element created.
 *
 * @param selector
 * @param callback
 * @since 4.2.7.1
 */
const lpOnElementReady = (selector, callback) => {
  const element = document.querySelector(selector);
  if (element) {
    callback(element);
    return;
  }
  const observer = new MutationObserver((mutations, obs) => {
    const element = document.querySelector(selector);
    if (element) {
      obs.disconnect();
      callback(element);
    }
  });
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });
};

// Parse JSON from string with content include LP_AJAX_START.
const lpAjaxParseJsonOld = data => {
  if (typeof data !== 'string') {
    return data;
  }
  const m = String.raw({
    raw: data
  }).match(/<-- LP_AJAX_START -->(.*)<-- LP_AJAX_END -->/s);
  try {
    if (m) {
      data = JSON.parse(m[1].replace(/(?:\r\n|\r|\n)/g, ''));
    } else {
      data = JSON.parse(data);
    }
  } catch (e) {
    data = {};
  }
  return data;
};

// status 0: hide, 1: show
const lpShowHideEl = (el, status = 0) => {
  if (!el) {
    return;
  }
  if (!status) {
    el.classList.add(lpClassName.hidden);
  } else {
    el.classList.remove(lpClassName.hidden);
  }
};

// status 0: hide, 1: show
const lpSetLoadingEl = (el, status) => {
  if (!el) {
    return;
  }
  if (!status) {
    el.classList.remove(lpClassName.loading);
  } else {
    el.classList.add(lpClassName.loading);
  }
};


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
/*!***********************************!*\
  !*** ./assets/src/js/loadAJAX.js ***!
  \***********************************/
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./utils.js */ "./assets/src/js/utils.js");
/* harmony import */ var _api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./api.js */ "./assets/src/js/api.js");
/**
 * Load all you need via AJAX
 *
 * @since 4.2.5.7
 * @version 1.0.4
 */




// Handle general parameter in the Frontend and Backend
const apiData = _api_js__WEBPACK_IMPORTED_MODULE_1__["default"].admin || _api_js__WEBPACK_IMPORTED_MODULE_1__["default"].frontend;
const urlAPI = apiData?.apiAJAX || '';
let lpSettings = {};
if ('undefined' !== typeof lpDataAdmin) {
  lpSettings = lpDataAdmin;
} else if ('undefined' !== typeof lpData) {
  lpSettings = lpData;
}
// End Handle general parameter in the Frontend and Backend

const lpAJAX = () => {
  return {
    autoLoadAPIs: () => {
      console.log('autoLoadAPIs');
    },
    fetchAPI: (url, params, callBack) => {
      const option = {
        headers: {}
      };
      if (0 !== parseInt(lpSettings.user_id)) {
        option.headers['X-WP-Nonce'] = lpSettings.nonce;
      }
      if ('undefined' !== typeof params.args.method_request) {
        option.method = params.args.method_request;
      } else {
        option.method = 'POST';
      }

      //params.args = { ...params.args, ...lpData.urlParams };

      if ('POST' === option.method) {
        option.body = JSON.stringify(params);
        option.headers['Content-Type'] = 'application/json';
      } else {
        params.args = JSON.stringify(params.args);
        params.callback = JSON.stringify(params.callback);
        url = (0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.lpAddQueryArgs)(url, params);
      }
      (0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.lpFetchAPI)(url, option, callBack);
    },
    fetchAJAX: (params, callBack, urlAjax = '') => {
      // Call via ajax.
      urlAjax = urlAjax || lpSettings.lpAjaxUrl;
      if (params.args.id_url) {
        urlAjax = (0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.lpAddQueryArgs)(urlAjax, {
          id_url: params.args.id_url
        });
      }
      const formData = new FormData();
      formData.append('nonce', lpSettings.nonce);
      formData.append('lp-load-ajax', 'load_content_via_ajax');
      formData.append('data', JSON.stringify(params));
      const dataSend = {
        method: 'POST',
        headers: {},
        body: formData
      };
      if (0 !== parseInt(lpSettings.user_id)) {
        dataSend.headers['X-WP-Nonce'] = lpSettings.nonce;
      }
      (0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.lpFetchAPI)(urlAjax, dataSend, callBack);
    },
    getElements: () => {
      // Finds all elements with the class '.lp-load-ajax-element'
      const elements = document.querySelectorAll('.lp-load-ajax-element:not(.loaded)');
      //console.log( 'getElements', elements );
      if (elements.length) {
        elements.forEach(element => {
          //console.log( 'Element handing', element );
          element.classList.add('loaded');
          let url = urlAPI;
          if (lpSettings.urlParams.hasOwnProperty('lang')) {
            url = (0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.lpAddQueryArgs)(url, {
              lang: lpSettings.urlParams.lang
            });
          }
          const elTarget = element.querySelector('.lp-target');
          if (!elTarget) {
            return;
          }
          const dataObj = JSON.parse(elTarget.dataset.send);
          const dataSend = {
            ...dataObj
          };
          const elLoadingFirst = element.querySelector('.loading-first');
          const callBack = {
            success: response => {
              const {
                status,
                message,
                data
              } = response;
              if ('success' === status) {
                elTarget.innerHTML = data.content;
              } else if ('error' === status) {
                elTarget.innerHTML = message;
              }
            },
            error: error => {
              console.log(error);
            },
            completed: () => {
              //console.log( 'completed' );
              if (elLoadingFirst) {
                elLoadingFirst.remove();
              }
            }
          };

          // Call via API
          //window.lpAJAXG.fetchAPI( url, dataSend, callBack );

          // Call via AJAX
          window.lpAJAXG.fetchAJAX(dataSend, callBack);
        });
      }
    }
  };
};
window.lpAJAXG = lpAJAX();
window.lpAJAXG.getElements();

// Listen element created
(0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.listenElementCreated)(node => {
  if (node.classList.contains('lp-load-ajax-element')) {
    //console.log( 'Element created', node );
    window.lpAJAXG.getElements();
  }
});

// Listen element ready
(0,_utils_js__WEBPACK_IMPORTED_MODULE_0__.lpOnElementReady)('.lp-load-ajax-element', element => {
  //console.log( 'Element ready', element );
  window.lpAJAXG.getElements();
});

// Case 2: readystatechange, find all elements with the class '.lp-load-ajax-element' not have class 'loaded'
document.addEventListener('readystatechange', event => {
  //console.log( 'readystatechange' );
  window.lpAJAXG.getElements();
});

// Case 3: DOMContentLoaded, find all elements with the class '.lp-load-ajax-element' not have class 'loaded'
document.addEventListener('DOMContentLoaded', () => {
  //console.log( 'DOMContentLoaded' );
  window.lpAJAXG.getElements();
});
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (lpAJAX);
/******/ })()
;
//# sourceMappingURL=loadAJAX.js.map