package eu.europa.ec.eurostat.basicservices.healthcare.cntr;

import java.util.ArrayList;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.healthcare.HCUtil;
import eu.europa.ec.eurostat.basicservices.healthcare.Validation;
import eu.europa.ec.eurostat.jgiscotools.geocoding.BingGeocoder;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.services.ServicesGeocoding;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.GeoData;
import eu.europa.ec.eurostat.jgiscotools.util.ProjectionUtil; 

public class EE {

	public static void main(String[] args) {		
		System.out.println("Start");

		//load data
		CSVFormat csvF = CSVFormat.DEFAULT.withFirstRecordAsHeader().withDelimiter(';');
		ArrayList<Map<String, String>> data = CSVUtil.load(HCUtil.path + "EE/EE_addr_formatted.csv", csvF);
		System.out.println(data.size());

		//geocode
		LocalParameters.loadProxySettings();
		ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		CSVUtil.addColumns(data, HCUtil.cols, "");
		//CSVUtil.addColumn(data, "ref_date", "22/05/2020");
		Validation.validate(data, "EE");
		CSVUtil.removeColumn(data, "address");

		// save
		System.out.println(data.size());
		CSVUtil.save(data, HCUtil.path + "EE/EE.csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HCUtil.path + "EE/EE.gpkg", ProjectionUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}