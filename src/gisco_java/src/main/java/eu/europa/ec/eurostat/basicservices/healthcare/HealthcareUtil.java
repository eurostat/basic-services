/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.healthcare;

import java.util.Collection;
import java.util.List;

import eu.europa.ec.eurostat.basicservices.BasicServicePublication.AttributeTypeSetter;
import eu.europa.ec.eurostat.basicservices.BasicServicesUtil;
import eu.europa.ec.eurostat.jgiscotools.feature.Feature;

/**
 * @author julien Gaffuri
 *
 */
public class HealthcareUtil {

	public static String path = BasicServicesUtil.path + "Service - Health/";

	//countries covered
	static String[] ccs = { "AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EL", "ES", "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SI", "SK"/* "UK"*/};

	//required attributes
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

	
	static AttributeTypeSetter ats = new AttributeTypeSetter() {
		public void setAttributeTypes(Collection<Feature> fs) {
			BasicServicesUtil.setAttributeTypeAsIntegerTypes(fs, "cap_beds", "cap_prac", "cap_rooms");
			BasicServicesUtil.setAttributeTypeAsDoubleTypes(fs, "lat", "lon");
		}
	};

}
