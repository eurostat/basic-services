package eu.europa.ec.eurostat.basicservices.education.cntr;

import java.util.ArrayList;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.ServicesGeocoding;
import eu.europa.ec.eurostat.basicservices.education.EducationUtil;
import eu.europa.ec.eurostat.basicservices.education.Validation;
import eu.europa.ec.eurostat.jgiscotools.geocoding.BingGeocoder;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.CRSUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.GeoData;

public class LU {

	public static void main(String[] args) {
		System.out.println("Start");

		// load data
		CSVFormat csvF = CSVFormat.DEFAULT.withFirstRecordAsHeader().withDelimiter(';');
		ArrayList<Map<String, String>> data = CSVUtil.load(EducationUtil.path + "LU/primary/export_eurostat.csv", csvF);

		System.out.println(data.size());

		//remove unused columns
		CSVUtil.removeColumn(data, "nb", "ecole");

		//rename columns
		CSVUtil.renameColumn(data, "eco_id", "id");
		CSVUtil.renameColumn(data, "nom", "name");
		CSVUtil.renameColumn(data, "num", "house_number");
		CSVUtil.renameColumn(data, "rue", "street");
		CSVUtil.renameColumn(data, "cpo", "postcode");
		CSVUtil.renameColumn(data, "ville", "city");
		CSVUtil.renameColumn(data, "total_st", "enrollment");

		for (Map<String, String> s : data) {

			//primaire = 1 if the school offers a primaire section
			String primaire = s.get("primaire");
			if(!"1".equals(primaire))
				System.out.println("Non primary school provided. Column 'primaire'=" + primaire);

			//levels

			//precoce = 1 if the school offers a precoce section
			String precoce = s.get("precoce");
			//prescol = 1 if the school offers a prescolaire section
			String prescol = s.get("prescol");

			if("1".equals(precoce) || "1".equals(prescol))
				s.put("levels", "0-1");
			else
				s.put("levels", "1");

			//public_private

			//pri = 1 if school is private
			String pri = s.get("pri");
			if("1".equals(pri))
				s.put("public_private", "private");
			else
				s.put("public_private", "public");

			//facility_type

			//int = 1 if school is international
			String int_ = s.get("int");
			if("1".equals(int_))
				s.put("facility_type", "international school");
			else
				s.put("facility_type", "");

		}
		CSVUtil.removeColumn(data, "precoce", "prescol", "primaire", "pri", "int");

		//add missing columns
		CSVUtil.addColumn(data, "fields", "");
		CSVUtil.addColumn(data, "max_students", "");
		CSVUtil.addColumn(data, "site_name", "");
		CSVUtil.addColumn(data, "email", "");
		CSVUtil.addColumn(data, "url", "");
		CSVUtil.addColumn(data, "comments", "");
		CSVUtil.addColumn(data, "cc", "LU");
		CSVUtil.addColumn(data, "country", "Luxembourg");
		CSVUtil.addColumn(data, "ref_date", "2021/02/15");
		CSVUtil.addColumn(data, "pub_date", "2021/02/15");

		//geocode
		LocalParameters.loadProxySettings();
		BingGeocoder.key = LocalParameters.get("bing_map_api_key");
		ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		Validation.validate(true, data, "LU");

		// save
		System.out.println(data.size());
		CSVUtil.save(data, EducationUtil.path + "LU/primary/LU_primary.csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), EducationUtil.path + "LU/primary/LU_primary.gpkg",
				CRSUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}
