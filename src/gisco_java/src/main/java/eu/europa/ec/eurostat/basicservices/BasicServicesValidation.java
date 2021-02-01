/**
 * 
 */
package eu.europa.ec.eurostat.basicservices;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.StringTokenizer;

import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;

/**
 * Validation for all basic services
 * 
 * @author gaffuju
 *
 */
public class BasicServicesValidation {

	//TODO detect duplicates?
	//those with exact same data
	//those with exact same data, but different ids
	//those with same name/site_name
	//those at the same location

	public static void validate(boolean showErrorMessage, Collection<Map<String, String>> data, String cc, List<String> cols_) {

		//check no presence of some columns besides the expected ones
		Set<String> ch = checkNoUnexpectedColumn(data, cols_);
		if(ch.size()>0) {
			System.err.println("Unexpected columns: ");
			System.err.println(ch);
		}

		boolean b;

		//id should be provided
		b = checkValuesNotNullOrEmpty(data, "id");
		if(!b) System.err.println("Identifier not provided for " + cc);

		//check id is provided and unique
		Set<String> dup = checkIdUnicity(data, "id");
		if(dup.size()>0) {
			System.err.println(dup.size() + " non unique identifiers for " + cc);
			for(String d : dup) System.out.print(d + ", ");
			System.out.println();
		}

		//check cc
		b = checkValuesAmong(showErrorMessage, data, "cc", cc);
		if(!b) System.err.println("Problem with cc values for " + cc);


		//check geo_qual -1,1,2,3,4
		b = checkValuesAmong(showErrorMessage, data, "geo_qual", "-1", "1", "2", "3", "4");
		if(!b) System.err.println("Problem with geo_qual values for " + cc);
		//check date format DD/MM/YYYY
		b = checkDateFormat(data, "ref_date", BasicServicesUtil.dateFormat);
		if(!b) System.err.println("Problem with ref_date format for " + cc);
		checkDateFormat(data, "pub_date", BasicServicesUtil.dateFormat);
		if(!b) System.err.println("Problem with pub_date format for " + cc);

		//non null columns
		b = checkValuesNotNullOrEmpty(data, "lat");
		if(!b) System.err.println("Missing values for lat format for " + cc);
		b = checkValuesNotNullOrEmpty(data, "lon");
		if(!b) System.err.println("Missing values for lon format for " + cc);
		b = checkValuesNotNullOrEmpty(data, "ref_date");
		if(!b) System.err.println("Missing values for ref_date format for " + cc);

		//check lon,lat extends
		checkGeoExtent(data, "lon", "lat");

	}

	public static void checkGeoExtent(Collection<Map<String, String>> data, String lonCol, String latCol) {
		for(Map<String, String> h : data) {
			String lon_ = h.get(lonCol);
			String lat_ = h.get(latCol);

			double lon = 0;
			try {
				lon = Double.parseDouble(lon_);
			} catch (NumberFormatException e) {
				System.err.println("Cannot decode longitude value " + lon_);
				continue;
			}
			double lat = 0;
			try {
				lat = Double.parseDouble(lat_);
			} catch (NumberFormatException e) {
				System.err.println("Cannot decode latitude value " + lat_);
				continue;
			}

			if(lat < -90.0 || lat > 90)
				System.err.println("Invalid latitude value: " + lat);
			if(lon < -180.0 || lon > 180)
				System.err.println("Invalid longitude value: " + lon);
		}
	}

	public static Set<String> checkIdUnicity(Collection<Map<String, String>> data, String idCol) {
		ArrayList<String> ids = CSVUtil.getValues(data, idCol);

		Set<String> duplicates = new LinkedHashSet<>();
		Set<String> uniques = new HashSet<>();
		for(String id : ids)
			if(!uniques.add(id)) duplicates.add(id);

		return duplicates;
	}

	public static boolean checkDateFormat(Collection<Map<String, String>> data, String col, SimpleDateFormat df) {
		for(Map<String, String> h : data) {
			String val = h.get(col);
			if(val == null || val.isEmpty())
				continue;
			try {
				df.parse(val);
			} catch (ParseException e) {
				//System.out.println("Could not parse date: " + val);
				return false;
			}
		}
		return true;
	}

	public static boolean checkValuesNotNullOrEmpty(Collection<Map<String, String>> data, String col) {
		for(Map<String, String> h : data) {
			String val = h.get(col);
			if(val == null || val.isEmpty())
				return false;
		}
		return true;
	}

	public static boolean checkValuesAmong(boolean showErrorMessage, Collection<Map<String, String>> data, String col, String... values) {
		return checkValuesAmongWithDelim(showErrorMessage, data, col, null, values);
	}

	public static boolean checkValuesAmongWithDelim(boolean showErrorMessage, Collection<Map<String, String>> data, String col, String delim, String... values) {
		for(Map<String, String> h : data) {
			String val_ = h.get(col);

			Iterator<Object> it = null;
			if(delim == null) {
				//make singleton
				ArrayList<Object> a = new ArrayList<Object>();
				a.add(val_);
				it = a.iterator();
			} else {
				//get list of values, based on delimiter
				it = new StringTokenizer(val_, delim).asIterator();
			}

			//check each value
			while(it.hasNext()) {
				Object val = it.next();
				boolean found = false;
				for(String v : values)
					if(val==null && v==null || v.equals(val)) {
						found=true; break;
					}
				if(!found) {
					if(showErrorMessage)
						System.err.println("Unexpected value '" + val + "' for column '" + col + "'");
					return false;
				}
			}

		}
		return true;
	}

	public static Set<String> checkNoUnexpectedColumn(Collection<Map<String, String>> data, Collection<String> cols) {
		for(Map<String, String> h : data) {
			Set<String> cs = new HashSet<>(h.keySet());
			cs.removeAll(cols);
			if(cs.size() != 0)
				return cs;
		}
		return new HashSet<String>();
	}

	/**
	 * Check a column has all values as integer numbers
	 * 
	 * @param showErrorMessage
	 * @param data
	 * @param col
	 * @return
	 */
	public static boolean checkIntValues(boolean showErrorMessage, Collection<Map<String, String>> data, String col) {
		for(Map<String, String> h : data) {
			String val = h.get(col);
			if(val == null) return false;
			if(val.length() == 0) continue;
			try {
				Integer.parseInt(val);
			} catch (NumberFormatException e) {
				if(showErrorMessage)
					System.err.println("Unepxected non-integer value for column "+col+". Value="+val);
				return false;
			}
		}
		return true;
	}

}
