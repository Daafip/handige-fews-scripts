function RunWorkflow([string]$wfId, [string]$T0, [string]$RestUri)
{
	$NotFinishedTasks 	= "P", "R", "" 
	Write-Output "Starting task $wfId with T0 = $T0"
	$InitTaskResponse = Invoke-WebRequest -Uri "$RestUri/runtask?workflowId=$wfId&timeZero=$T0" -Method POST -UseBasicParsing
	$TaskId = $InitTaskResponse.Content
	# Wait for task to finish
	Start-Sleep -s 5
	$Taskresponse = Invoke-WebRequest -Uri "$RestUri/taskrunstatus?taskId=$TaskId" -Method GET -UseBasicParsing
	DO {
		Start-Sleep -s 5
		$Taskresponse = Invoke-WebRequest -Uri "$RestUri/taskrunstatus?taskId=$TaskId" -Method GET -UseBasicParsing
	} While ($Taskresponse.Content -in $NotFinishedTasks)
}