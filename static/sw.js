const CACHE_NAME = 'vowvault-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// Install event - cache resources
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      }
    )
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push notification event
self.addEventListener('push', event => {
  console.log('Service Worker: Push event received');
  
  if (event.data) {
    try {
      const data = event.data.json();
      console.log('Service Worker: Push data:', data);
      
      const options = {
        body: data.message || 'You have a new notification!',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-32x32.png',
        tag: 'vowvault-notification',
        requireInteraction: false,
        silent: false,
        data: data
      };

      event.waitUntil(
        self.registration.showNotification(data.title || 'VowVault Notification', options)
      );
    } catch (error) {
      console.error('Service Worker: Error parsing push data:', error);
      // Fallback notification
      const options = {
        body: 'You have a new notification from VowVault!',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-32x32.png',
        tag: 'vowvault-notification'
      };
      
      event.waitUntil(
        self.registration.showNotification('VowVault Notification', options)
      );
    }
  } else {
    console.log('Service Worker: No data in push event');
    // Default notification
    const options = {
      body: 'You have a new notification from VowVault!',
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/icon-32x32.png',
      tag: 'vowvault-notification'
    };
    
    event.waitUntil(
      self.registration.showNotification('VowVault Notification', options)
    );
  }
});

// Notification click event
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification clicked');
  event.notification.close();
  
  // Get the notification data
  const notificationData = event.notification.data;
  
  // Navigate to the appropriate page based on notification type
  let targetUrl = '/notifications';
  
  if (notificationData && notificationData.content_type && notificationData.content_id) {
    if (notificationData.content_type === 'photo') {
      targetUrl = `/photo/${notificationData.content_id}`;
    } else if (notificationData.content_type === 'message') {
      targetUrl = `/messages#message-${notificationData.content_id}`;
    }
  }
  
  event.waitUntil(
    clients.openWindow(targetUrl)
  );
});

// Background sync for offline uploads (if supported)
self.addEventListener('sync', event => {
  console.log('Service Worker: Background sync triggered:', event.tag);
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Handle offline uploads when connection is restored
  console.log('Service Worker: Background sync processing');
  // This could be used to sync offline uploads when connection is restored
} 