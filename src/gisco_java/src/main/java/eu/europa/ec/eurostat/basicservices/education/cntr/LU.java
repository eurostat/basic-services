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

		CSVUtil.removeColumn(data, "nb");
		CSVUtil.removeColumn(data, "ecole");

		CSVUtil.renameColumn(data, "eco_id", "id");
		CSVUtil.renameColumn(data, "nom", "name");
		CSVUtil.renameColumn(data, "num", "house_number");
		CSVUtil.renameColumn(data, "rue", "street");
		CSVUtil.renameColumn(data, "cpo", "postcode");
		CSVUtil.renameColumn(data, "ville", "city");
		CSVUtil.renameColumn(data, "total_st", "enrollment");

		CSVUtil.addColumn(data, "cc", "LU");




		/*"precoce";"prescol";"primaire";"pri";"int"
		precoce = 1 if the school offers a precoce section
				prescol = 1 if the school offers a prescolaire section
				primaire = 1 if the school offers a primaire section
						pri = 1 if school is private
						int = 1 if school is international*/

		/*
		Collection<Map<String, String>> schoolsFormatted = new ArrayList<Map<String, String>>();
		for (Map<String, String> s : data) {

			// new formatted school
			HashMap<String, String> sf = new HashMap<String, String>();

			// copy columns
			sf.put("id", s.get("INSTITUTION_ID"));
			sf.put("name", s.get("INSTITUTION_NAME"));
			sf.put("levels", s.get("LEVEL OF EDUCATION"));
			sf.put("facility_type", s.get("SCHOOL TYPE"));
			sf.put("enrollment", s.get("ENROLLMENT"));
			sf.put("email", s.get("EPOST"));
			sf.put("url", s.get("URL"));
			sf.put("postcode", s.get("POSTCODE"));
			sf.put("city", s.get("SETTLEMENT"));


			// address 
			//Kooli tänav, 1
			String ad = sf.get("ADDRESS");

			//if ad contains a comma, split it. else put address in street
			if (ad.contains(",")) {
				String[] parts = ad.split(",");
				String houseNumber = parts[1];
				sf.put("house_number", houseNumber);
				String street = parts[0];
				sf.put("street", street);

				if (parts.length != 2)
					System.err.println(ad);
			}
			else {	
				sf.put("street", s.get("ADDRESS"));
			}



			// add to list
			schoolsFormatted.add(sf);

			// geocode
			LocalParameters.loadProxySettings();
			ServicesGeocoding.set(BingGeocoder.get(), schoolsFormatted, "lon", "lat", true, true);
		 */

		Validation.validate(true, data, "LU");

		// save
		System.out.println(data.size());
		CSVUtil.save(data, EducationUtil.path + "LU/primary/LU.csv");
		//GeoData.save(CSVUtil.CSVToFeatures(schoolsFormatted, "lon", "lat"), EducationUtil.path + "EE/EE.gpkg",
		//		CRSUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}
