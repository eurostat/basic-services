package eu.europa.ec.eurostat.basicservices.education.cntr;

import java.util.ArrayList;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.education.EducationUtil;
import eu.europa.ec.eurostat.basicservices.education.Validation;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;

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

			//levels

			//precoce = 1 if the school offers a precoce section
			String precoce = s.get("precoce");
			//prescol = 1 if the school offers a prescolaire section
			String prescol = s.get("prescol");
			//primaire = 1 if the school offers a primaire section
			String primaire = s.get("primaire");
			System.out.println(precoce);

			//public_private

			//pri = 1 if school is private
			String pri = s.get("pri");

			//facility_type
			
			//int = 1 if school is international*/
			String int_ = s.get("int");



		}
		CSVUtil.removeColumn(data, "precoce", "prescol", "primaire", "pri", "int");

		//add missing columns
		CSVUtil.addColumn(data, "max_students", "");
		CSVUtil.addColumn(data, "site_name", "");
		CSVUtil.addColumn(data, "email", "");
		CSVUtil.addColumn(data, "url", "");
		CSVUtil.addColumn(data, "comments", "");
		CSVUtil.addColumn(data, "cc", "LU");
		CSVUtil.addColumn(data, "country", "Luxembourg");
		CSVUtil.addColumn(data, "ref_date", "2021/02/15");
		CSVUtil.addColumn(data, "pub_date", "2021/02/15");

		//TODO geocode
		CSVUtil.addColumn(data, "lon", "0");
		CSVUtil.addColumn(data, "lat", "0");
		CSVUtil.addColumn(data, "geo_qual", "-1");
		//LocalParameters.loadProxySettings();
		//ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		Validation.validate(true, data, "LU");

		// save
		System.out.println(data.size());
		CSVUtil.save(data, EducationUtil.path + "LU/primary/LU.csv");
		//GeoData.save(CSVUtil.CSVToFeatures(schoolsFormatted, "lon", "lat"), EducationUtil.path + "EE/EE.gpkg",
		//		CRSUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}
