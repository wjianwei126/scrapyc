function kill_job (task_id) {
    $.getJSON("/task/kill?task_id="+task_id,{},function(data,status){

            alert(data.msg);
  })
}
function stop_job (task_id) {
    $.getJSON("/task/stop/"+task_id,{},function(data,status){

            alert(data.msg);
  })
}
function modify_cronjob (job_id) {
    $.getJSON("/cronjob_modify?job_id="+job_id,function(data,status){

            alert(data.msg);
  })
}
function pause_cronjob (job_id) {
    $.getJSON("/cronjob_pause?job_id="+job_id,{},function(data,status){

            alert(data.msg);
  })
}
function remove_cronjob (job_id) {
    $.getJSON("/cronjob_remove?job_id="+job_id,{},function(data,status){

            alert(data.msg);
  })
}



function load_module_page (ele_id,url) {
    // body...
    $.post(url,{},function  (data,status) {
        if (status == "success"){
            $("#"+ele_id).html(data)
            
        }
        // body...
    })
}
