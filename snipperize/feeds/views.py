from django.shortcuts import render_to_response

def latest_feed_proxy(request):
    return render_to_response('feeds/latest_feed_proxy.html')