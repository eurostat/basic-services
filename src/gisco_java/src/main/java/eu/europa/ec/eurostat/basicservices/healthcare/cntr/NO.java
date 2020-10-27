/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.healthcare.cntr;

import java.util.ArrayList;
import java.util.Map;

import eu.europa.ec.eurostat.basicservices.healthcare.HCUtil;
import eu.europa.ec.eurostat.basicservices.healthcare.Validation;
import eu.europa.ec.eurostat.jgiscotools.geocoding.BingGeocoder;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.services.ServicesGeocoding;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.GeoData;
import eu.europa.ec.eurostat.jgiscotools.util.ProjectionUtil;

/**
 * @author gaffuju
 *
 */
public class NO {

	static String cc = "NO";

	public static void main(String[] args) {

		//load input data
		ArrayList<Map<String, String>> data = CSVUtil.load(HCUtil.path + "NO/CSV/NO_from_Web.csv");
		System.out.println(data.size());

		CSVUtil.removeColumn(data, "Besøksadresse");
		CSVUtil.addColumn(data, "ref_date", "01/01/2020");

		LocalParameters.loadProxySettings();
		ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		CSVUtil.addColumns(data, HCUtil.cols, "");
		Validation.validate(data, cc);
		CSVUtil.save(data, HCUtil.path+cc + "/"+cc+".csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HCUtil.path+cc + "/"+cc+".gpkg", ProjectionUtil.getWGS_84_CRS());

	}
}
