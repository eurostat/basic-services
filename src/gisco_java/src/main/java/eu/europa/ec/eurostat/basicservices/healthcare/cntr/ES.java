/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.healthcare.cntr;

import java.util.ArrayList;
import java.util.Map;

import eu.europa.ec.eurostat.basicservices.ServicesGeocoding;
import eu.europa.ec.eurostat.basicservices.healthcare.HealthcareUtil;
import eu.europa.ec.eurostat.basicservices.healthcare.HealthcareValidation;
import eu.europa.ec.eurostat.jgiscotools.geocoding.BingGeocoder;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.CRSUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.GeoData;

/**
 * @author gaffuju
 *
 */
public class ES {

	static String cc = "ES";

	public static void main(String[] args) {

		//load input data
		ArrayList<Map<String, String>> data = CSVUtil.load(HealthcareUtil.path+cc + "/"+cc+"_formated.csv");
		System.out.println(data.size());

		LocalParameters.loadProxySettings();
		ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		CSVUtil.addColumns(data, HealthcareUtil.cols, "");
		HealthcareValidation.validate(data, cc, HealthcareUtil.cols_);
		CSVUtil.save(data, HealthcareUtil.path+cc + "/"+cc+".csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HealthcareUtil.path+cc + "/"+cc+".gpkg", CRSUtil.getWGS_84_CRS());

	}
}
