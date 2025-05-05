// ==UserScript==
// @name         Auto Next Episode on Vidsrc (Stable Check)
// @namespace    http://tampermonkey.net/
// @version      1.8
// @description  Auto-increment episode number when video ends, inject jwplayer-dependent code via script tag.
// @match        https://vidsrc.cc/v2/embed/tv/*
// @grant        GM_openInTab
// @run-at       document-start
// ==/UserScript==

(function () {
  'use strict';

  function injectJWPlayerFunctions() {
      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.textContent = `
          (function() {
              let jwp = null;

              function setCookie(name, value, days) {
                  const expires = new Date(Date.now() + days * 864e5).toUTCString();
                  document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
              }

              function getCookie(name) {
                  return document.cookie.split('; ').reduce((r, v) => {
                      const parts = v.split('=');
                      return parts[0] === name ? decodeURIComponent(parts[1]) : r
                  }, '');
              }

              function waitForStableVideo(callback) {
                  let foundCount = 6;
                  const checkInterval = setInterval(() => {
                      const video = document.querySelector("video");
                      if (video) {
                          video.preload = "auto";
                      }
                      if (!window.jwplayer) {
                          console.log("JWPlayer not available yet.");
                          return;
                      }
                      const jwplayer = window.jwplayer();
                      if (jwplayer) {
                          jwp = jwplayer;
                          console.log("JWPlayer instance found.");
                      }
                      if (video) {
                          foundCount--;
                      }
                      if (jwp) {
                          callback(video);
                          let savedRate = parseFloat(getCookie('playbackRate'));
                          if (isNaN(savedRate)) savedRate = 1.75;
                          jwp.setPlaybackRate(savedRate);
                          jwp.setCaptions({
                              "fontSize": "12",
                              "fontFamily": "Verdana",
                              "color": "#ffffff",
                              "backgroundColor": "#000000",
                              "backgroundOpacity": 10,
                              "edgeColor ": "#ffffff",
                              "fontOpacity": 70,
                              "edgeStyle": "uniform"
                          });
                          monitorBuffering(video);
                          clearInterval(checkInterval);
                      }
                  }, 500);
              }

              function setupVideoEvents(video) {
                  console.log("Video confirmed. Setting playback rate and binding 'ended' event.");
                  video.addEventListener("ended", () => {
                      const url = new URL(window.location.href);
                      const pathSegments = url.pathname.split("/");
                      const currentEpisode = parseInt(pathSegments[pathSegments.length - 1], 10);
                      if (isNaN(currentEpisode)) {
                          console.warn("Could not find episode number in URL.");
                          return;
                      }
                      const nextEpisode = currentEpisode + 1;
                      pathSegments[pathSegments.length - 1] = nextEpisode.toString();
                      url.pathname = pathSegments.join("/");
                      console.log("Redirecting to next episode:", url.toString());
                      window.location.href = url.toString();
                  });
              }

              function monitorBuffering(video) {
                  let lastTime = video.currentTime;
                  let stuckStart = null;
                  let playStart = Date.now();
                  let qualityList = jwp.getQualityLevels();
                  let qualityIndex = jwp.getCurrentQuality();

                  const checkBuffer = setInterval(() => {
                      if (!jwp || video.ended || video.paused) return;

                      if (video.currentTime === lastTime) {
                          if (!stuckStart) stuckStart = Date.now();
                          const stuckDuration = Date.now() - stuckStart;

                          if (stuckDuration > 5000 && qualityIndex < qualityList.length - 1) {
                              qualityIndex++;
                              jwp.setCurrentQuality(qualityIndex);
                              console.log("Increased quality to index:", qualityIndex);
                              stuckStart = null;
                              playStart = Date.now();
                          }
                      } else {
                          if (Date.now() - playStart > 10000 && qualityIndex > 0) {
                              qualityIndex--;
                              jwp.setCurrentQuality(qualityIndex);
                              console.log("Decreased quality to index:", qualityIndex);
                              playStart = Date.now();
                          }
                          stuckStart = null;
                      }
                      lastTime = video.currentTime;
                  }, 1000);
              }

              document.addEventListener("DOMContentLoaded", function () {
                  waitForStableVideo(setupVideoEvents);
              });

              document.addEventListener("keydown", function(event) {
                  if (!jwp) return;
                  if (event.key === "]") {
                      let newRate = jwp.getPlaybackRate() + 0.05;
                      jwp.setPlaybackRate(newRate);
                      setCookie('playbackRate', newRate, 7);
                  }
                  if (event.key === "[") {
                      let newRate = jwp.getPlaybackRate() - 0.05;
                      jwp.setPlaybackRate(newRate);
                      setCookie('playbackRate', newRate, 7);
                  }
                  if (event.key === "p") {
                      jwp.setPlaybackRate(1);
                      setCookie('playbackRate', 1, 7);
                  }
              });
          })();
      `;
      document.documentElement.appendChild(script);
  }

  // Inject jwplayer-dependent script
  injectJWPlayerFunctions();

  // Keep GM_openInTab feature in userscript only
  document.addEventListener("keydown", function(event) {
      if (event.key === "s" || event.key === "S") {
          const text = document.querySelector("div.title").textContent;
          const query = encodeURIComponent(text);
          GM_openInTab(`https://www.google.com/search?q=${query}`, { active: false });
      }
  });
})();


// // ==UserScript==
// // @name         Auto Next Episode on Vidsrc (Stable Check)
// // @namespace    http://tampermonkey.net/
// // @version      1.2
// // @description  Auto-increment episode number when video ends, after confirming player exists 3 times. Sets speed to 1.75x.
// // @match        https://vidsrc.cc/v2/embed/tv/*
// // @grant        GM_openInTab
// // @run-at       document-start
// // ==/UserScript==

// (function () {
//     'use strict';
//     let jwp = null;
//     // let wof = window.open;
//     function waitForStableVideo(callback) {

//         let foundCount = 6;
//         // let lastVideo = null;

//         const checkInterval = setInterval(() => {
//             const video = document.querySelector("video");
//             // alert(video);
//             if (!window.jwplayer) {
//               console.log("Not found yet");
//               return;
//             }
//             const jwplayer = window.jwplayer();
//             // const jwplayer = unsafeWindow.jwplayer(unsafeWindow.jwplayer().getContainer());
//             // alert(jwp);
//             if (jwplayer) {
//               jwp = jwplayer;
//               alert("found JWP");
//             }
//             if (video) {
//                 foundCount--;
//                 // lastVideo = video;
//                 // console.log(`Video found (${foundCount}/3)...`);
//             }

//             if (jwp) {
//                 callback(video);
//                 jwp.setPlaybackRate(1.75);
//                   jwp.setCaptions({
//                       "fontSize": "12",
//                       "fontFamily": "Verdana",
//                       "color": "#ffffff",
//                       "backgroundColor": "#000000",
//                       "backgroundOpacity": 10,
//                       "edgeColor ": "#ffffff",
//                       "fontOpacity": 70,
//                       "edgeStyle": "uniform"
//                   });
//                 clearInterval(checkInterval);
//             }
//         }, 500);
//     }

//     function setupVideoEvents(video) {
//         console.log("Video confirmed. Setting playback rate and binding 'ended' event.");

//         // video.playbackRate = 1.75;

//         video.addEventListener("ended", () => {
//             const url = new URL(window.location.href);
//             const pathSegments = url.pathname.split("/");

//             const currentEpisode = parseInt(pathSegments[pathSegments.length - 1], 10);
//             if (isNaN(currentEpisode)) {
//                 console.warn("Could not find episode number in URL.");
//                 return;
//             }

//             const nextEpisode = currentEpisode + 1;
//             pathSegments[pathSegments.length - 1] = nextEpisode.toString();
//             url.pathname = pathSegments.join("/");

//             console.log("Redirecting to next episode:", url.toString());
//             window.location.href = url.toString();
//         });
//     }

//     // Entry point
//     document.addEventListener("DOMContentLoaded", function () {
//         waitForStableVideo(setupVideoEvents);
//     });
//     document.addEventListener("keydown", function(event) {
//       // alert(event.key, jwp);
//       if (event.key === "[") {
//         jwp.setPlaybackRate(jwp.getPlaybackRate()+0.5);
//       }
//       if (event.key === "]") {
//         jwp.setPlaybackRate(jwp.getPlaybackRate()-0.5);
//       }
//       if (event.key === "p") {
//         jwp.setPlaybackRate(1);
//       }
//       // Check if the pressed key is "s" or "S"
//       if (event.key === "s" || event.key === "S") {
//         // Retrieve the text from the DOM element
//         const text = document.querySelector("div.title").textContent;

//         // Encode the text to ensure it's a valid URL component
//         const query = encodeURIComponent(text);

//         // Open a new Google search with the text
//         // alert("opening "+ `https://www.google.com/search?q=${query}`);
//         // window.open(`https://www.google.com/search?q=${query}`, "_blank");
//         // wof(`https://www.google.com/search?q=${query}`, "_blank");
//        GM_openInTab(`https://www.google.com/search?q=${query}`,{ active: false});
//       }
//     });
//     document.addEventListener("keydown", function(event) {
//       // Check if the pressed key is "s" or "S"
//       if (event.key === "s" || event.key === "S") {
//         // Retrieve the text from the DOM element
//         const text = document.querySelector("div.title").textContent;

//         // Encode the text to ensure it's a valid URL component
//         const query = encodeURIComponent(text);

//         // Open a new Google search with the text
//         // alert("opening "+ `https://www.google.com/search?q=${query}`);
//         // window.open(`https://www.google.com/search?q=${query}`, "_blank");
//         // wof(`https://www.google.com/search?q=${query}`, "_blank");
//        GM_openInTab(`https://www.google.com/search?q=${query}`,{ active: false});
//       }
//     });
// })();


