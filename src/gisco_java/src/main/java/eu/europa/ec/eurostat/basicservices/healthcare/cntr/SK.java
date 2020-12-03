package eu.europa.ec.eurostat.basicservices.healthcare.cntr;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Map;

import eu.europa.ec.eurostat.basicservices.healthcare.HealthcareUtil;
import eu.europa.ec.eurostat.basicservices.healthcare.Validation;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.CRSUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.GeoData; 

public class SK {

	public static void main(String[] args) {
		System.out.println("Start");

		//load data
		ArrayList<Map<String, String>> data = CSVUtil.load(HealthcareUtil.path + "SK/SK_formatted.csv");
		System.out.println(data.size());
		
		DateTimeFormatter dtf = DateTimeFormatter.ofPattern("dd/MM/yyyy");  
		LocalDateTime now = LocalDateTime.now();  
		CSVUtil.setValue(data, "pub_date", (dtf.format(now)));

		CSVUtil.addColumn(data, "comments", "");
		
		LocalParameters.loadProxySettings();
	//	ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		CSVUtil.addColumns(data, HealthcareUtil.cols, "");
		Validation.validate(true, data, "SK");

		// save
		System.out.println(data.size());
		CSVUtil.save(data, HealthcareUtil.path + "SK/SK.csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HealthcareUtil.path + "SK/SK.gpkg", CRSUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}