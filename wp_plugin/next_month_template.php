<?php
/*
Template Name: Next month 2
*/
/**
 * The template for displaying daily Saints and Readings
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/#single-post
 *
 * @package St_Constantine2
 *    <form action="https://yorkorthodox.org/tsr"><button type="submit" value="Go to next Month" /></form>
 */

get_header();

?>
  	<div id="primary" class="content-area">
   <main id="main" class="site-main" role="main">
   <h2>Next Month's Saints and Readings</h2>
<?php

        $upload_dir = wp_upload_dir();
        $upload_path = $upload_dir['basedir'];
        $yocal_db_path = $upload_path . '/yocal/YOCal_Master.db';

        // FUNCTION TO RETURN FULL ROW OF DATA FOR A GIVEN DATE
        // ==================================================== 
        if (!function_exists('read_data')) {
    function read_data($d) {
        global $yocal_db_path;
        try {
            $db = new SQLite3($yocal_db_path, SQLITE3_OPEN_READONLY);
            $stmt = $db->prepare('SELECT * FROM yocal_main WHERE date = :date');
            $stmt->bindValue(':date', $d, SQLITE3_TEXT);
            $result = $stmt->execute();
            $row = $result->fetchArray(SQLITE3_ASSOC);
            $db->close();
            return (object)$row;
        } catch (Exception $e) {
            echo $e->getMessage() . "\n";
            return null;
        }
    }
        }

        // FUNCTION TO RETURN FULL ROW OF DATA FOR A GIVEN MONTH
        // ==================================================== 
        if (!function_exists('read_data_month')) {
    function read_data_month($m, $y) {
        global $yocal_db_path;
        try {
            $db = new SQLite3($yocal_db_path, SQLITE3_OPEN_READONLY);
            $stmt = $db->prepare('SELECT * FROM yocal_main WHERE month = :month and year = :year');
            $stmt->bindValue(':month', $m, SQLITE3_TEXT);
            $stmt->bindValue(':year', $y, SQLITE3_TEXT);
            $result = $stmt->execute();
            $rows = [];
            while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
                $rows[] = (object)$row;
            }
            $db->close();
            return $rows;
        } catch (Exception $e) {
            echo $e->getMessage() . "\n";
            return null;
        }
    }

}

if (!function_exists('read_lect')) {
    function read_lect($c) {
        global $yocal_db_path;
        try {
            $db = new SQLite3($yocal_db_path, SQLITE3_OPEN_READONLY);
            $stmt = $db->prepare('SELECT * FROM yocal_lections WHERE code = :code');
            $stmt->bindValue(':code', $c, SQLITE3_TEXT);
            $result = $stmt->execute();
            $row = $result->fetchArray(SQLITE3_ASSOC);
            $db->close();
            return (object)$row;
        } catch (Exception $e) {
            return null;
        }
    }
}

if (!function_exists('format_data_monthly')) {
    function format_data_monthly($r)   {
       // Set variables for each field of data:
       $day_name = $r->day_name;
       $day_num = $r->day_num;
       $day_ord = $r->ord;
       $month_name = $r->month;
       $year = $r->year;
       $fast = $r->fast;
       $tone = $r->tone;
       $eoth = $r->eothinon;
       $desig_a = $r->desig_a;
       $desig_g = $r->desig_g;
       $major = $r->major_commem;
       $foreafter = $r->fore_after;
       $basil = $r->basil;
       $global = $r->class_5;
       $british = $r->british;
       
       // Date in full:

       $txt1 = '<h3 margin-bottom:0px>'.$day_name.' '.$day_ord.' '.$month_name.' '.$year.'</h3>';

       // Fasting, Tone, Eothinon, Liturgy of St Basil:
   
       $txt2 = '';

       if (strlen($fast)>1) {
          $txt2 = $fast."<br>";
       }
    
       if (strlen($tone)>1) {
          $txt2 .= $tone." - ".$eoth."<br>";
       }
    
       if (strlen($basil)>1) {
          $txt2 .= $basil."<br>";
       }    

       if (strlen($txt2)>1) {
          $txt2 = '<h4 class="lectionary-single-subtitle">'.$txt2.'</h4>';
       }  
      
       // Designations, Major Commemorations, Fore- and After-feasts:
   
       $txt3 = '';

       if (strlen($desig_a)>1) {
          $txt3 = $desig_a;
          if (strlen($desig_g)>1) {
             $txt3 .= ", ".$desig_g;
          }
          $txt3 .= "<br>";
       }
   
       if (strlen($major)>1) {
          $txt3 .= $major."<br>";
       }

       if (strlen($foreafter)>1) {
          $txt3 .= $foreafter."<br>";
       }
   
       if (strlen($txt3)>1) {
          $txt3 = '<b>'.$txt3."</b>";
       }
   
       // Minor commemorations including those of Britain and Ireland:
 
       $txt4 = '<em>Commemorations:</em><br>'.$global;
 
           if (strlen($british)>1) {
              $txt4 .= '<br><em>British Isles and Ireland: </em><br>'.$british;
           }
 
       // Return the assembled text
  
       $text = $txt1.$txt2.$txt3.$txt4;

       return $text."<br>";
    }
}

if (!function_exists('format_lect')) {
        function format_lect($l)   {        
           // $lects is for the list of lection references
           // $texts is for the full text of the readings 
 
           $lects = "<em>Readings:</em><br>";
           
           // Set variables for each field of data:

           $a_code = $l->a_code;
           $g_code = $l->g_code;
           if ($g_code == $a_code) {
               $g_code = "";
           }
           $is_apos = $l->is_comm_apos;
           $is_gosp = $l->is_comm_gosp;
           $c_code = $l->c_code;
           $x_code = $l->x_code;           
 
           // Get data for each code in turn: Apostle, Gospel, Extra and Commemoration

           if (strlen($a_code)>1) {
               $a_data = read_lect($a_code);
               $a_lect_1 = $a_data->lect_1;
               $a_lect_2 = $a_data->lect_2;
          }

           // Deal with F7EC where only the Apostle reading is used
           if ($a_code == "F7EC") {
               $a_lect_2 = "";
           }

           if (strlen($g_code)>1) {
               $g_data = read_lect($g_code);
               $g_lect_2 = $g_data->lect_2;
           }
           if (strlen($x_code)>1) {
               $x_data = read_lect($x_code);
               $x_lect_1 = $x_data->lect_1;
               $x_lect_2 = $x_data->lect_2;
           } 
           if (strlen($c_code)>1) {
               $c_data = read_lect($c_code);
               $c_lect_1 = $c_data->lect_1;
               $c_lect_2 = $c_data->lect_2;
           }

           // If there is a commemoration, embolden the primary readings 
           // If no commemoration, embolden the readings of the day 

           if (strlen($c_code)>1) {  
               if ($is_apos == 1) {
                  $c_lect_1 = "<b>".$c_lect_1."</b>";
               } else {
                  $a_lect_1 = "<b>".$a_lect_1."</b>";
               } 
               if ($is_gosp == 1) {
                  $c_lect_2 = "<b>".$c_lect_2."</b>";
               } elseif (strlen($a_lect_2)>1) {
                  $a_lect_2 = "<b>".$a_lect_2."</b>";
               } elseif (strlen($g_lect_2)>1) {
                  $g_lect_2 = "<b>".$g_lect_2."</b>"; 
               } 
           } else {
               $a_lect_1 = "<b>".$a_lect_1."</b>";
               if (strlen($a_lect_2)>1) {
                  $a_lect_2 = "<b>".$a_lect_2."</b>";
               } elseif (strlen($g_lect_2)>1) {
                  $g_lect_2 = "<b>".$g_lect_2."</b>"; 
               }
           }    

           // Assemble the various Lections

           if (strlen($a_lect_1)>1) {
               $lects .= $a_lect_1;
               if ((strlen($a_lect_2)>1) or (strlen($g_code)>1)) {
                  $lects .= "; ";
               } else {
                  $lects .= "<br>";
               }
           }
           if (strlen($a_lect_2)>1) {
               $lects .= $a_lect_2."<br>";
           }
           if (strlen($g_lect_2)>1) {
               $lects .= $g_lect_2."<br>";
           }
           if (strlen($c_lect_1)>1) {
               $lects .= "<em>For the Commemoration: </em>".$c_lect_1."; ".$c_lect_2."<br>";
            }
           if (strlen($x_lect_1)>1) {
               $lects .= $x_lect_1;
               if (strlen($x_lect_2)>1) {
                  $lects .= "; ".$x_lect_2."<br>";
                  $texts .= $x_text_2;
               } else {
                  $lects .= "<br>";
               }
           }

           // As there is no Liturgy Mon-Fri in Lent, remove the bold tags from the lections

           if ((substr($a_code,0,1) == "G") and (substr($a_code,2,1) != "S")) {
                $lects = str_replace("<b>","",$lects);
                $lects = str_replace("</b>","",$lects);
           }


           // Finally, return the assembled Lections and Texts
               
           $rtn = $lects;
           return $rtn;
        }
}

        // DISPLAY THE DATA FOR THE MONTH
        // ==============================

        // Get the date variables
        $thismonth = strtotime(date('Y-m')."-01");
        $nextmonth = strtotime("+1 month", $thismonth);
        $Yr = date('Y', $nextmonth);
        $Y = (int)$Yr;
        $M = date('F', $nextmonth);
        $Mn = date('m', $nextmonth);        


        // Display the link to view the following month
        $following = "https://www.yorkorthodox.org/this-month/";
        echo "<a href=$following>... or view this month's Saints and Readings</a><br>";

        // Display the heading: Month and Year
        $header = "<h2>".$M." ".$Yr."</h2>";
        echo $header;
        
        // Display 'From the Fathers' text if available
        $ffile = "documents/".date('Y-m').'_fathers.txt';
        if (file_exists($ffile)) {
           $fathers = fopen($ffile, "r");
           echo fread($fathers,filesize($ffile));
           fclose($fathers);
        }

        // Display the Fasting Guidelines and Readings in Bold expanatory text
        echo "<em><b>Fasting Guidelines:</b></em><br>
On days designated <em>strict fast</em> we abstain from dairy products, meat, fish, oil and wine.
Some seafoods, e.g. squid, crab, roe and prawn, are permitted.<br><br>";
        echo "<em>Readings in <b>bold type</b> are those appointed by the Typikon for use at the Liturgy</em><br>";
        // Get the data for the whole month
        $rows = read_data_month($M, $Y);

        // Reset the main page text variable
        $all_txt = "";

        // Cycle through the rows, using the functions to format the data for each day 
        foreach ($rows as $row)  {
           $data = "";
           $data = format_data_monthly($row);
           $data .= format_lect($row);

           // Update page text
           $all_txt .= $data."<br>";
        }        

        echo $all_txt;

        // Display PDF links if the files are available
        $A4file = "https://www.yorkorthodox.org/documents/".date('Y-m').'_A4.pdf';
        $A5file = "https://www.yorkorthodox.org/documents/".date('Y-m').'_A5.pdf';
        if (file_exists("documents/".date('Y-m').'_A4.pdf')) {
           echo "A copy of this calendar, suitable for printing, is available <a href=$A4file>here</a> in PDF format. For those with appropriate printing facilities a version is available <a href=$A5file>here</a> as an A5 booklet.<br><br>";
        }

        // Display the Acknowledgements text if available
        $Ackfile = "documents/Acknowledgements.txt";
        if (file_exists($Ackfile)) {
           $Ack = fopen($Ackfile, "r");
           echo fread($Ack,filesize($Ackfile));
           fclose($Ack);
        }
  ?>
       

		</main><!-- #main -->
	</div><!-- #primary -->

<?php
//get_sidebar();
get_footer();
