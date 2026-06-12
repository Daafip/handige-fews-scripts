function RunWorkflow([string]$wfId, [string]$startTime, [string]$endTime, [string]$RestUri)
{
	$NotFinishedTasks 	= "P", "R", "" 
	Write-Output "Starting task $wfId with startTime = $startTime; endTime = $endTime"
	$InitTaskResponse = Invoke-WebRequest -Uri "$RestUri/runtask?workflowId=$wfId&timeZero=$startTime&startTime=$startTime&endTime=$endTime" -Method POST -UseBasicParsing
	$TaskId = $InitTaskResponse.Content
	# Wait for task to finish
	Start-Sleep -s 5
	$Taskresponse = Invoke-WebRequest -Uri "$RestUri/taskrunstatus?taskId=$TaskId" -Method GET -UseBasicParsing
	DO {
		Start-Sleep -s 5
		$Taskresponse = Invoke-WebRequest -Uri "$RestUri/taskrunstatus?taskId=$TaskId" -Method GET -UseBasicParsing
	} While ($Taskresponse.Content -in $NotFinishedTasks)
}