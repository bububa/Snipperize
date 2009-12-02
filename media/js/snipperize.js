var Snipperize = Class.create();
Snipperize.prototype = {
    initialize: function ()
    {
        this.AjaxPath="/ajax/";
        this.pid = 0;
        this.preview_size = 10;
        var self = this;
        self.resize();
        Event.observe(window, 'resize', function (){
            self.resize();
        });
    },
    
    resize: function()
    {
        var self = this;
        mainHeight = $('divFooter').cumulativeOffset().top - $('divNavTop').getHeight();
        $('divLeftNav').setStyle({height: mainHeight/2 + 'px'});
        $('divLeft').setStyle({height:mainHeight + 'px'});
        $('divPreview').setStyle({height: self.preview_size + 'px'});
        $('divListings').setStyle({height:(mainHeight - $('divPreview').getHeight()) + 'px'});
        $('divMain').setStyle({height:mainHeight + 'px'});
    },
    
    initFavButtons: function()
    {
        var self = this;
        $$('a.fav_button').each(function(a){
            if (a.title!='signin please')
            {
                a.observe('click', function(){
                    self.add_to_fav(a);
                    return false;
                });
            }
        });
        
        $$('a.unfav_button').each(function(a){
            a.observe('click', function(){
                self.del_from_fav(a);
                return false;
            });
        });
    },
    
    add_to_fav: function(a)
    {
        var self = this;
        var url = a.href;
        var myAjax = new Ajax.Request(
            url,
            {
                method: 'get',
                onComplete: function(resp)
                {
                    var info = resp.responseText;
                    if (info == -1)
                    {
                        alert('Permission denied!');
                    }else if(info == -2){
                    	alert('Signin first!');
                    }else{
                        a.removeClassName('fav_button');
                        a.addClassName('unfav_button');
                        a.update('Delete from favorite');
                        a.observe('click', function(){
                            self.del_from_fav(a);
                            return false;
                        });
                    }
                }
            }
        );
    },
    
    del_from_fav: function(a)
    {
        var self = this;
        var url = a.href;
        var myAjax = new Ajax.Request(
            url,
            {
                method: 'get',
                onComplete: function(resp)
                {
                    var info = resp.responseText;
                    if (info == -1)
                    {
                        alert('Permission denied!');
                    }else if(info == -2){
                    	alert('Signin first!');
                    }else{
                        a.removeClassName('unfav_button');
                        a.addClassName('fav_button');
                        a.update('Add to favorite');
                        a.observe('click', function(){
                            self.add_to_fav(a);
                            return false;
                        });
                    }
                }
            }
        );
    }
}