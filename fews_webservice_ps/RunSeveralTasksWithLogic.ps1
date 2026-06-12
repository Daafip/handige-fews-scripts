Set-ExecutionPolicy -ExecutionPolicy Unrestricted
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

. .\RunWorkflowStartEnd.ps1

$startDate	 = Get-Date -Date "2025-12-31 00:00:00Z"
$endDate	 = Get-Date -Date "2026-01-04 00:00:00Z"
$workflowIds = @('wf.0',
				 'wf.1',
				 'wf.1.corrected',
                 'wf.2',
                 'wf.3')	

$start = $startDate
$DATA_SERVICES_URL = 'http://localhost:8080/FewsWebServices/rest/fewspiservice/v1'
for($end = $startDate.AddDays(3); $end -le $endDate; $end = $end.AddDays(3)) {
	$startStr = "$($start.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
	$endStr = "$($end.ToString("yyyy-MM-ddTHH:mm:ssZ"))"

	# run model 
	Foreach ($workflowId in $workflowIds) {
		# mswap is one behind
		if ($workflowId -eq 'wf.1' -or $workflowId -eq 'wf.1.corrected') {
			$startMswap = $start.AddDays(-1)
			$endMwap = $end.AddDays(-1)
			$startMswapStr = "$($startMswap.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
			$endMswapStr = "$($endMwap.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
			RunWorkflow $workflowId $startMswapStr $endMswapStr $DATA_SERVICES_URL # 29 - 31
		}
        # run model 'normal time'
        if ($workflowId -eq 'wf.2' -or $workflowId -eq 'wf.3') {
			RunWorkflow $workflowId $startStr $endStr $DATA_SERVICES_URL # 29 - 01
		}
        # first time step to import is one along 
        else {
        	$startModflow = $start.AddDays(1)
			$endModflow = $end # end time stays the same
			$startModflowStr = "$($startModflow.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
			$endModflowStr = "$($endModflow.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
			RunWorkflow $workflowId $startModflowStr $endModflowStr $DATA_SERVICES_URL # 30 - 1
        }
		
	}

	$start = $end
}

