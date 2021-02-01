package eu.europa.ec.eurostat.basicservices.education.cntr;

import java.util.ArrayList;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.education.EducationUtil;
import eu.europa.ec.eurostat.basicservices.education.Validation;
import eu.europa.ec.eurostat.basicservices.healthcare.HealthcareUtil;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.CRSUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.GeoData;

public class IE {

	public static void main(String[] args) {
		System.out.println("Start");

		// load data
		CSVFormat csvF = CSVFormat.DEFAULT.withFirstRecordAsHeader().withDelimiter(',');
		ArrayList<Map<String, String>> data = CSVUtil.load(EducationUtil.path + "IE/IE_formatted.csv", csvF);

		System.out.println(data.size());
		
		CSVUtil.addColumns(data, EducationUtil.cols, "");
		CSVUtil.setValue(data, "cc", "IE");
		CSVUtil.setValue(data, "geo_qual", "4");
		CSVUtil.setValue(data, "ref_date", "30/6/2020");

		//TODO why is this not removing the column?
		CSVUtil.removeColumn(data, "Attribute");


		Validation.validate(true, data, "IE");

		// save
		System.out.println(data.size());
		CSVUtil.save(data, EducationUtil.path + "IE/IE.csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), EducationUtil.path + "IE/IE.gpkg",
				CRSUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}