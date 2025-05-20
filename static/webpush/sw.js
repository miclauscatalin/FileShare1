self.addEventListener('push', function(event) {
    var data = event.data.json();
    event.waitUntil(
        self.registration.showNotification(data.head, {
            body: data.body,
            icon: data.icon,
            data: { url: data.url }
        })
    );
});
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    if (event.notification.data && event.notification.data.url) {
        event.waitUntil(clients.openWindow(event.notification.data.url));
    }
});
