Set-ExecutionPolicy -ExecutionPolicy Unrestricted
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

. .\RunWorkflowStartEnd.ps1

$startDate	 = Get-Date -Date "2025-12-05 00:00:00Z"
$endDate	 = Get-Date -Date "2025-12-18 00:00:00Z"
$workflowIds = @('wf.1') 

$start = $startDate
$DATA_SERVICES_URL = 'http://localhost:8080/FewsWebServices/rest/fewspiservice/v1'
for($end = $startDate.AddDays(1); $end -le $endDate; $end = $end.AddDays(1)) {
	$startStr = "$($start.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
	$endStr = "$($end.ToString("yyyy-MM-ddTHH:mm:ssZ"))"

	Foreach ($workflowId in $workflowIds) {
		RunWorkflow $workflowId $startStr $endStr $DATA_SERVICES_URL
	}

	$start = $end
}

