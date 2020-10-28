/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.healthcare;

import java.util.Collection;
import java.util.List;

import eu.europa.ec.eurostat.basicservices.BasicServicesUtil;
import eu.europa.ec.eurostat.jgiscotools.feature.Feature;

/**
 * @author julien Gaffuri
 *
 */
public class HealthcareUtil {

	public static String path = BasicServicesUtil.path + "Service - Health/";

	//country codes covered
	static String[] ccs = { "AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK"/* "UK"*/};

	//CSV columns
	public static String[] cols = {
			"id", "hospital_name", "site_name",
			"lat", "lon", "geo_qual",
			"street", "house_number", "postcode", "city", "cc", "country",
			"cap_beds", "cap_prac", "cap_rooms",
			"emergency", "facility_type", "public_private", "list_specs",
			"tel", "email", "url",
			"ref_date", "pub_date",
			"comments"
	};
	public static List<String> cols_ = List.of(cols);

	//
	static void applyTypes(Collection<Feature> fs) {
		for(Feature f : fs) {
			for(String att : new String[]{"cap_beds", "cap_prac", "cap_rooms"}) {
				var v = f.getAttribute(att);
				if(v==null) continue;
				if("".equals(v)) f.setAttribute(att, null);
				else f.setAttribute(att, Integer.parseInt(v.toString()));
			}
			for(String att : new String[] {"lat", "lon"}) {
				var v = f.getAttribute(att);
				if(v==null) continue;
				if("".equals(v)) f.setAttribute(att, null);
				else f.setAttribute(att, Double.parseDouble(v.toString()));
			}
		}
	}



	/*
	static void geocodeGISCO(ArrayList<Map<String,String>> hospitals, boolean usePostcode, boolean printURLQuery) {
		//int count = 0;
		int fails = 0;
		for(Map<String,String> hospital : hospitals) {
			//count++;
			String address = "";
			if(hospital.get("house_number")!=null) address += hospital.get("house_number") + " ";
			address += hospital.get("street");
			address += " ";
			if(usePostcode) {
				address += hospital.get("postcode");
				address += " ";
			}
			address += hospital.get("city");
			address += " ";
			address += hospital.get("country");
			System.out.println(address);

			GeocodingResult gr = GISCOGeocoder.geocode(address, printURLQuery);
			Coordinate c = gr.position;
			System.out.println(c  + "  --- " + gr.matching + " --- " + gr.confidence);
			if(c.getX()==0 && c.getY()==0) fails++;

			//if(count > 10) break;
			hospital.put("latGISCO", "" + c.y);
			hospital.put("lonGISCO", "" + c.x);
			hospital.put("geo_qual", "" + gr.quality);
			hospital.put("geo_matchingGISCO", "" + gr.matching);
			hospital.put("geo_confidenceGISCO", "" + gr.confidence);
		}

		System.out.println("Failures: " + fails + "/" + hospitals.size());
	}
	 */

	/*public static void CSVToGPKG(String cc) {
		ArrayList<Map<String, String>> data = CSVUtil.load(HealthcareUtil.path + cc+"/"+cc+".csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HealthcareUtil.path + cc+"/"+cc+".gpkg", CRSUtil.getWGS_84_CRS());
	}*/

}
