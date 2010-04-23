wmd_options = { autostart: false };
    
var instances = [];

function createWMD(textarea_id, preview_id) {
	if (!Attacklab || !Attacklab.wmd) {
		return;
	}
	var textarea = document.getElementById(textarea_id)
	var previewDiv = document.getElementById(preview_id)
	
	var panes = {input:textarea, preview:previewDiv, output:null};
    var manager = new Attacklab.wmd.previewManager(panes);
	var editor = new Attacklab.wmd.editor(textarea, manager.refresh);
}