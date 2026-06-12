import pandas as pd
import requests


def main(): 
    base_url = "http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/"


    endpoint = "timeseries?"

    params = dict(
        filterId="..",
        moduleInstanceIds="...",
        parameterIds="...",
        startTime="1990-01-01T00:00:00Z",
        endTime="2026-01-01T00:00:00Z",
        onlyHeaders="true",
        showStatistics="true",
        documentFormat="PI_JSON",
        omitOriginalUnreliable="false",
        omitEmptyTimeSeries="false",
        omitCorrectedUnreliable="false",
        omitMissing="false",
    )

    res = requests.get(base_url + endpoint, params=params)
    data = res.json()

    df = pd.json_normalize(data["timeSeries"], sep="_")
    cols = df.columns
    df.rename(
        columns=dict(zip(cols, ("_".join(col.split("_")[1:]) for col in cols))),
        inplace=True,
    )
    df = df.drop(
        columns=[
            "type",
            "moduleInstanceId",
            "timeStep_unit",
            "timeStep_multiplier",
            "startDate_date",
            "startDate_time",
            "endDate_date",
            "endDate_time",
            "missVal",
            "units",
            "lat",
            "lon",
            # zelfde als lastvalue
            #'lastValueTime_date', 
            #'lastValueTime_time' 
        ]
    )
    df_sub = df.dropna(subset="firstValueTime_date").copy()
    df_sub['firstValueTime'] = df_sub.apply(lambda x: pd.Timestamp(str(x.firstValueTime_date) +" "+ str(x.firstValueTime_time)),axis=1)
    df_sub['lastValueTime'] = df_sub.apply(lambda x: pd.Timestamp(str(x.lastValueTime_date) +" "+ str(x.lastValueTime_time)),axis=1)
    df_sub = df_sub.drop(columns=['firstValueTime_date', 'firstValueTime_time', 'lastValueTime_date', 'lastValueTime_time'])
    df_sub.to_csv("metadata_ontzorgd_meting.csv")


if __name__ == "__main__":
    main()