(function($){
jQuery.center_block = function(div_id) {
    var selector_id = "#" + div_id;
    var box = jQuery(selector_id);
    var w = jQuery(window); 
    var top = w.scrollTop() + Math.max((w.height() - box.height()) / 2, 0);
    var left = w.scrollLeft() + Math.max((w.width() - box.width()) / 2, 0);
    var obj = new Object;
    obj.top = top;
    obj.left = left;
    return obj;	 
};

jQuery.center_element = function(parent_id, div_id) {
    var selector_id = "#" + div_id;
    var box = jQuery(selector_id);
    var w = jQuery("#" + parent_id); 
    var top = Math.max((w.height() - box.height()) / 2, 0);
    var left = Math.max((w.width() - box.width()) / 2, 0);
    var obj = new Object;
    obj.top = top;
    obj.left = left;
    return obj;	 
};

jQuery.center_element_in_window = function(parent, child) {
    var box = child;
    var w = parent; 
    var top = Math.max((w.height() - box.height()) / 2, 0);
    var left = Math.max((w.width() - box.width()) / 2, 0);
    var obj = new Object;
    obj.top = top;
    obj.left = left;
    return obj;	 
};

})(jQuery);
