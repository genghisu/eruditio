{% autoescape off %}
<script type="text/javascript">	
(function($) {
jQuery.encode_relatedcontent_data = function(content_type, object_id) {
	var final_data = "(" + content_type + " " + object_id + ")"
	return final_data;
}

jQuery.get_relatedcontent_object = function(content_type, object_id) {
	var object_name = "relatedcontent_item_" + content_type + "_" + object_id;
	return object_name;
}

jQuery.update_target_call = function(target_id, data_id, ajax_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id) {
	parent.jQuery.update_target(target_id, data_id, ajax_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id);
}

jQuery.update_target = function(target_id, data_id, ajax_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id) {
	jQuery.get(ajax_url, {base_content_type:base_content_type, 
						  base_object_id:base_object_id, selectable_content_type:selectable_content_type, 
						  selectable_object_id:selectable_object_id, target_id:target_id, data_id:data_id},
			function(data) {
				var target_object = jQuery('#' + target_id);
				target_object.append(data);
			}
	);
}

jQuery.modify_content_association = function(association_url, base_content_type, base_object_id, selectable_content_type,
		selectable_object_id, usage, add) {
	jQuery.get(association_url, {base_content_type:base_content_type, base_object_id:base_object_id, selectable_content_type:selectable_content_type,
		selectable_object_id:selectable_object_id, usage:usage, add:add});
}

jQuery.remove_from_target = function(target_id, associate_url, base_content_type, base_object_id, selectable_content_type, selectable_object_id, usage) {
	var object_name = jQuery.get_relatedcontent_object(selectable_content_type, selectable_object_id);
	var object = jQuery('#' + object_name);
	if (associate_url) {
		$.get(associate_url, {base_content_type:base_content_type, base_object_id:base_object_id, selectable_content_type:selectable_content_type,
			selectable_object_id:selectable_object_id, usage:usage, add:"false"});
	}
	object.fadeOut("slow", function(){
		object.remove();
	});
}

jQuery.remove_from_data = function(data_id, content_type, object_id) {
	var data_object = jQuery('#' + data_id);
	var current_data = data_object.val();
	var target_data = jQuery.encode_relatedcontent_data(content_type, object_id);
	var final_data = current_data.replace(target_data, "")
	data_object.val(final_data);
}

jQuery.update_data_call = function(data_id, content_type, object_id) {
	parent.jQuery.update_data(data_id, content_type, object_id);
}

jQuery.update_data = function(data_id, content_type, object_id) {
	var data_object = jQuery('#' + data_id);
	var current_data = data_object.val();
	var final_data = current_data + "," + jQuery.encode_relatedcontent_data(content_type, object_id);
	data_object.val(final_data);
}

jQuery.disable_update = function(link_id, row_id) {
	var link_object = jQuery('#' + link_id);
	var row_object = jQuery('#' + row_id);
	link_object.unbind();
	row_object.fadeTo("slow", "0.30");
}

jQuery.check_related_item = function(data_id, content_type, object_id, row_id, link_id) {
	var link_object = jQuery('#' + link_id);
	var row_object = jQuery('#' + row_id);
	var data_object = jQuery('#' + data_id, parent.document.body);
	var current_data = data_object.val();
	var look_up = jQuery.encode_relatedcontent_data(content_type, object_id);
	if (current_data.indexOf(look_up) >= 0) {
		link_object.unbind();
		row_object.fadeTo("slow", "0.30");
	}
}
})(jQuery);
</script>
{% endautoescape %}