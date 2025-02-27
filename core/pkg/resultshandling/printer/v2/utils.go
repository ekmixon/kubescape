package v2

import (
	"github.com/armosec/k8s-interface/workloadinterface"
	"github.com/armosec/kubescape/v2/core/cautils"
	"github.com/armosec/kubescape/v2/core/cautils/logger"
	"github.com/armosec/kubescape/v2/core/cautils/logger/helpers"
	"github.com/armosec/opa-utils/reporthandling"
	"github.com/armosec/opa-utils/reporthandling/results/v1/reportsummary"
	"github.com/armosec/opa-utils/reporthandling/results/v1/resourcesresults"
	reporthandlingv2 "github.com/armosec/opa-utils/reporthandling/v2"
)

// finalizeV2Report finalize the results objects by copying data from map to lists
func FinalizeResults(data *cautils.OPASessionObj) *reporthandlingv2.PostureReport {
	report := reporthandlingv2.PostureReport{
		SummaryDetails:       data.Report.SummaryDetails,
		ClusterAPIServerInfo: data.Report.ClusterAPIServerInfo,
		ReportGenerationTime: data.Report.ReportGenerationTime,
		Attributes:           data.Report.Attributes,
		ClusterName:          data.Report.ClusterName,
		CustomerGUID:         data.Report.CustomerGUID,
		ClusterCloudProvider: data.Report.ClusterCloudProvider,
	}

	report.Results = make([]resourcesresults.Result, len(data.ResourcesResult))
	finalizeResults(report.Results, data.ResourcesResult)

	report.Resources = finalizeResources(report.Results, data.AllResources, data.ResourceSource)

	return &report
}
func finalizeResults(results []resourcesresults.Result, resourcesResult map[string]resourcesresults.Result) {
	index := 0
	for resourceID := range resourcesResult {
		results[index] = resourcesResult[resourceID]
		index++
	}
}

type infoStars struct {
	stars string
	info  string
}

func mapInfoToPrintInfo(controls reportsummary.ControlSummaries) []infoStars {
	infoToPrintInfo := []infoStars{}
	infoToPrintInfoMap := map[string]interface{}{}
	starCount := "*"
	for _, control := range controls {
		if control.GetStatus().IsSkipped() && control.GetStatus().Info() != "" {
			if _, ok := infoToPrintInfoMap[control.GetStatus().Info()]; !ok {
				infoToPrintInfo = append(infoToPrintInfo, infoStars{
					info:  control.GetStatus().Info(),
					stars: starCount,
				})
				starCount += starCount
				infoToPrintInfoMap[control.GetStatus().Info()] = nil
			}
		}
	}
	return infoToPrintInfo
}

func finalizeResources(results []resourcesresults.Result, allResources map[string]workloadinterface.IMetadata, resourcesSource map[string]reporthandling.Source) []reporthandling.Resource {
	resources := make([]reporthandling.Resource, 0)
	for i := range results {
		if obj, ok := allResources[results[i].ResourceID]; ok {
			resource := *reporthandling.NewResourceIMetadata(obj)
			if r, ok := resourcesSource[results[i].ResourceID]; ok {
				resource.SetSource(&r)
			}
			resources = append(resources, resource)
		}
	}
	return resources
}

func logOUtputFile(fileName string) {
	if fileName != "/dev/stdout" && fileName != "/dev/stderr" {
		logger.L().Success("Scan results saved", helpers.String("filename", fileName))
	}

}
