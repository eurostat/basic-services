/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.education;

import java.util.Collection;
import java.util.List;

import eu.europa.ec.eurostat.basicservices.BasicServicePublication.AttributeTypeSetter;
import eu.europa.ec.eurostat.basicservices.BasicServicesUtil;
import eu.europa.ec.eurostat.jgiscotools.feature.Feature;

/**
 * @author gaffuju
 *
 */
public class EducationUtil {

	public static String path = BasicServicesUtil.path + "Service - Education/";

	//countries covered
	static String[] ccs = { "NL", "IE", "SI", "SK" };

	//required attributes
	public static String[] cols = {
			"id", "name", "site_name",
			"lat", "lon", "geo_qual",
			"street", "house_number", "postcode", "city", "cc", "country",
			"levels", "max_students", "enrollment",
			"fields", "facility_type", "public_private",
			"tel", "email", "url",
			"ref_date", "pub_date",
			"comments"
	};
	public static List<String> cols_ = List.of(cols);

	static AttributeTypeSetter ats = new AttributeTypeSetter() {
		public void setAttributeTypes(Collection<Feature> fs) {
			BasicServicesUtil.setAttributeTypeAsIntegerTypes(fs, "max_students", "enrollment", "levels");
			BasicServicesUtil.setAttributeTypeAsDoubleTypes(fs, "lat", "lon");
		}
	};

}
